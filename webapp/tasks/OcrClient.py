import pika, uuid, os, time

class OcrClient():
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
        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.queue_broker))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send(self, ocr_request):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(ocr_request))
        while self.response is None:
            self.connection.process_data_events()
        return self.response
