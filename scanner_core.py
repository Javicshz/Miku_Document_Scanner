from pathlib import Path
import cv2
import imutils
from skimage.filters import threshold_local
from pyimagesearch.transform import four_point_transform


def scan_documents(image_path, preview=False):
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    ratio = image.shape[0] / 500.0
    original = image.copy()
    resized = imutils.resize(image, height=500)

    # Make the image easier to edge detect.
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # Find the four corners of the page.
    page_contour = find_page_contour(edged, gray)
    if page_contour is None:
        raise RuntimeError(f"Could not find page outline: {image_path}")

    # Warp the original full-size image.
    warped = four_point_transform(original, page_contour.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    # Turn the page into a high-contrast black and white scan.
    threshold = threshold_local(warped, 11, offset=10, method="gaussian")
    scanned = (warped > threshold).astype("uint8") * 255

    return scanned


def find_page_contour(edged, gray):
    # Ignore tiny four-point contours from individual words or letters.
    min_page_area = gray.shape[0] * gray.shape[1] * 0.20

    contour = find_four_point_contour(edged, cv2.RETR_LIST, min_area=min_page_area)
    if contour is not None:
        return contour

    # Fallback for white paper on a dark background.
    _, paper = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    paper = cv2.morphologyEx(paper, cv2.MORPH_CLOSE, kernel, iterations=2)
    return find_four_point_contour(paper, cv2.RETR_EXTERNAL, min_area=min_page_area)


def find_four_point_contour(image, retrieval_mode, min_area=0):
    contours = cv2.findContours(image.copy(), retrieval_mode, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            return approx

    return None
