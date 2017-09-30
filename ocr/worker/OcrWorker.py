import pika, os, time

class OcrWorker():
    queue_broker = "rabbitmq"
    queue_name = 'ocr_queue'


    def __init__(self):
        response = os.system("ping -c 1 " + self.queue_broker)

        # and then check the response...
        while response != 0:
            print(self.queue_broker, 'ping...')
            response = os.system("ping -c 1 " + self.queue_broker)
            time.sleep(2)

        print(self.queue_broker, 'is up!')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.queue_broker))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue_name)

        print(" [x] Awaiting OCR requests")
        self.channel.start_consuming()

    def process(self, payload):
        # get image
        image = "some image"
        return self.get_text(image)


    def get_text(self, image):
        # do ocr
        extracted_text = "fertsch"
        return extracted_text


    def on_request(self, ch, method, props, body):
        payload = body

        print(" [.] processing:" % payload)
        response = self.process(payload)

        ch.basic_publish(exchange='',
                      routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                        body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
