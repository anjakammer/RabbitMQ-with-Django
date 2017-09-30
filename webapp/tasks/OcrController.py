import json
from OcrClient import OcrClient

ocr_client = OcrClient()

ocr_request = {
    "id" : "",
    "image_url" : ""
}
response = ocr_client.get_text_from_image(ocr_request)
print(" [.] Got %s" % json.loads(response))
