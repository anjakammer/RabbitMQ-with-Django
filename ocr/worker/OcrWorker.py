import pika, time, json, os

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

        channel.start_consuming()

    def __process(self, payload):
        # get image
        self.__get_text(payload)
        return {
            "id": "",
            "image_url": ""
        }

    def __get_text(self, image):
        # do ocr
        extracted_text = image
        return extracted_text


    def __on_request(self, ch, method, props, body):
        payload = body

        print(" [.] processing:" % payload)
        response = self.__process(payload)

        ch.basic_publish(exchange='',
                      routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                        body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
