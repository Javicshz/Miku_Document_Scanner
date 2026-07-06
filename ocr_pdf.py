from pathlib import Path
from tempfile import TemporaryDirectory
import cv2
import pytesseract
from pypdf import PdfWriter
from scanner_core import scan_documents

def images_to_searchable_pdf(image_paths, output_pdf_path):
    # normalize the output path to create a pdf writer
    output_pdf_path = Path(output_pdf_path)
    writer = PdfWriter()

    # temporarydictionary creates a scracth folder and deletes it automatically
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        for page_number, image_path in enumerate(image_paths, start=1):
            # scan one image into a clean black white page image
            scanned = scan_documents(image_path)

            # tesseract works well when given an actual image file path
            temp_image = temp_dir / f"page_{page_number}.png"
            temp_pdf = temp_dir / f"page_{page_number}.pdf"

            cv2.imwrite(str(temp_image), scanned)

            # ask tesseract to create a searchable pdf page
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                str(temp_image),
                extension="pdf",
                config="--psm 6",
            )
            temp_pdf.write_bytes(pdf_bytes)

            # add this one page pdf into the final combined pdf
            writer.append(str(temp_pdf))

        # write all collected pages into the final output file
        with output_pdf_path.open("wb") as f:
            writer.write(f)