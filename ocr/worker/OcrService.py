from PIL import Image
import pytesseract, cv2, os, re

class OcrService():
    TESSDATA_DIR_CONFIG = '--tessdata-dir "/usr/share/tesseract-ocr"'
    CHARS_TO_REMOVE = '[^\w\d_äÄöÖüÜß+\-(){}|\,\.\\n!?<>]+'

    def extract_text_from_image(self, image_path):
        normalized_image = self.__pre_processing(image_path)

        text = pytesseract.image_to_string(Image.open(normalized_image), lang='deu', config=self.TESSDATA_DIR_CONFIG)

        self.__remove_resources(image_path, normalized_image)

        decoded_string = re.sub(self.CHARS_TO_REMOVE, ' ', text).strip().replace('\n', '\\n')

        return decoded_string

    def __remove_resources(self, *args):
        for resource in args:
            os.remove(resource)

    def __pre_processing(self, source_image):
        image = cv2.imread(source_image, 0)

        gray = cv2.threshold(image, 0, 255,
                             cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        output = "{}.png".format(os.getpid())
        cv2.imwrite(output, gray)

        return output