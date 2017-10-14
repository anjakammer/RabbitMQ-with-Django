import pika, time, json, os, ipfsapi
from .OcrService import OcrService

class OcrWorker():
    QUEUE_BROKER = os.getenv('QUEUE_BROKER')
    QUEUE_NAME = 'ocr_' + os.getenv('QUEUE_NAME')

    def __init__(self):
        server_down = True
        while server_down:
            try:
                self.__connect()
                server_down = False
                print(self.QUEUE_BROKER, 'is up!')
            except:
                server_down = True
                print('Cannot connect to %s try again in 2 Sek.' % self.QUEUE_BROKER)
                time.sleep(2)

    def __connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.QUEUE_BROKER))
        channel = connection.channel()

        channel.queue_declare(queue=self.QUEUE_NAME)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.__on_request, queue=self.QUEUE_NAME)

        print(" [x] Awaiting OCR requests")

        try:
            channel.start_consuming()
        except:
            print(OcrWorker.__name__, 'restarts. Error occurred while listening to', self.QUEUE_BROKER)

    def __process(self, request):
        file_hash = request.get('file_hash')
        self.__load_image(file_hash)

        image_path = self.__load_image(file_hash)
        extracted_text = "processing error"
        try:
            ocr_service = OcrService()
            extracted_text = ocr_service.extract_text_from_image(image_path)
        except BaseException as e:
            print('Failed to use', OcrService.__name__, 'with error: ', str(e))

        return {
            "id": request.get('id'),
            "result": extracted_text
        }

    def __load_image(self, file_hash):
        api = ipfsapi.connect('127.0.0.1', 5001)
        api.get(file_hash)

        return file_hash

    def __on_request(self, ch, method, props, body):
        request_string = body.decode('unicode_escape')
        print(" [.] processing:", request_string)

        request_object = json.loads(request_string)

        response = self.__process(request_object)

        ch.basic_publish(exchange='',
                      routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                        body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
