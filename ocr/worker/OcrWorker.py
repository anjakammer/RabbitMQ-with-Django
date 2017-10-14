import pika, time, json, os, ipfsapi, logging, sys
from .OcrService import OcrService

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class OcrWorker():
    QUEUE_BROKER = os.getenv('QUEUE_BROKER')
    QUEUE_NAME = 'ocr_' + os.getenv('QUEUE_NAME')
    IPFS_HOST = '127.0.0.1'
    IPFS_API_PORT = 5001

    KEY_PROCESSING_ERROR = 'processing error'

    def __init__(self):
        server_down = True
        while server_down:
            try:
                self.__connect()
                server_down = False
                logging.info('%s is up!', self.QUEUE_BROKER)
            except:
                server_down = True
                logging.warning('Cannot connect to %s try again in 2 Sec.', self.QUEUE_BROKER)
                time.sleep(2)

    def __connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.QUEUE_BROKER))
        channel = connection.channel()

        channel.queue_declare(queue=self.QUEUE_NAME)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.__on_request, queue=self.QUEUE_NAME)

        logging.info('[x] Awaiting OCR requests')

        try:
            channel.start_consuming()
        except:
            logging.error('%s restarts. Error occurred while listening to %s', OcrWorker.__name__, self.QUEUE_BROKER)

    def __on_request(self, ch, method, props, body):
        request_string = body.decode('unicode_escape')
        logging.info('[.] processing: %s' % request_string)

        request_object = json.loads(request_string)
        response = self.__process(request_object)

        ch.basic_publish(exchange='',
                      routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                        body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __process(self, request):
        file_hash = request.get('file_hash')
        self.__load_image(file_hash)

        image_path = self.__load_image(file_hash)
        extracted_text = self.KEY_PROCESSING_ERROR
        try:
            ocr_service = OcrService()
            extracted_text = ocr_service.extract_text_from_image(image_path)
        except BaseException as e:
            logging.error('Failed to use %s with error: %s', OcrService.__name__, str(e))

        return {
            "id": request.get('id'),
            "result": extracted_text
        }

    def __load_image(self, file_hash):
        file_storage = ipfsapi.connect(self.IPFS_HOST, self.IPFS_API_PORT)
        file_storage.get(file_hash)

        return file_hash
