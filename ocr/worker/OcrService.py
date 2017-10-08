from PIL import Image
import pytesseract
import cv2
import os, re


class OcrService():
    TESSDATA_DIR_CONFIG = '--tessdata-dir "/usr/share/tesseract-ocr"'
    REGEX_ALLOWED_CHARS = '[^\w\d_äÄöÖüÜß+\-(){}|\,\.\\n!?<>]+'

    def extract_text_from_image(self, image_path):
        image = cv2.imread(image_path, 0)

        gray = cv2.threshold(image, 0, 255,
                cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)

        text = pytesseract.image_to_string(Image.open(filename), lang='deu', config=self.TESSDATA_DIR_CONFIG)
        os.remove(filename)

        decoded_string = re.sub(self.REGEX_ALLOWED_CHARS, ' ', text).strip().replace('\n', '\\n')

        return decoded_string
