from PIL import Image
import pytesseract
import cv2
import os

class OcrService():
    def __init__(self):
        image = cv2.imread('worker/example_01.png',0)

        gray = cv2.threshold(image, 0, 255,
                cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)

        text = pytesseract.image_to_string(Image.open(filename))
        print(text)
