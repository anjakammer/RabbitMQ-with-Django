import pika, time, json, os, ast

class OcrWorker():
    QUEUE_BROKER = os.getenv('QUEUE_BROKER')
    QUEUE_NAME = os.getenv('OCR_QUEUE_NAME')

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
        # get image from hash
        image = request
        self.__get_text(image)
        # put result into dict
        id = request.get('id')
        return {
            "id": id,
            "result": "fertiger Text hier"
        }

    def __get_text(self, image):
        # do ocr
        time.sleep(10)
        extracted_text = image
        return extracted_text


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
