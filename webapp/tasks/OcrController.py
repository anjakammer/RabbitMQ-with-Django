from OcrClient import OcrClient

ocr_client = OcrClient()

ocr_request = {
    "id" : "",
    "image_url" : ""
}
print(" [x] Requesting ocr")
response = ocr_client.send(ocr_request)
print(" [.] Got %r" % response)