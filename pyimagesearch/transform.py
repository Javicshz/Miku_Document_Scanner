import numpy as np
import cv2

def order_points(pts):
    # this will initialize the points, top left, top right, bottom left, bottom right
    rect = np.zeros((4, 2), dtype="float32")

    # the top left is will have the smallest sum, bottom right will have the largest
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now compute the difference between the points, the top right will be the
    # smallest difference where as the bottom left will have the largest
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of points and unpack them individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the image which will be the max distance between br and bl
    # x coordinates or the tr and tl x coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image which will be the max sitance between
    # tr, br y coordinates or the top left and botom left y coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now with the new dimenstions of the new image, construct the set of destination
    # points to get the birds eye view.
    dst = np.array([
        [0,0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped
