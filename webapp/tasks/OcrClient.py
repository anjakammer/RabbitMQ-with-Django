import pika, uuid, time, json

class OcrClient():
    QUEUE_BROKER = "rabbitmq"
    QUEUE_NAME = 'ocr_queue'

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
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.QUEUE_BROKER))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.__on_response, no_ack=False,
                                   queue=self.callback_queue)

    def __on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get_text_from_image(self, ocr_request):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        print(" [x] Requesting ocr for %s" % ocr_request)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.QUEUE_NAME,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                       delivery_mode=2,  # make message persistent
                                       content_type='application/json',
                                   ),
                                   body=json.dumps(ocr_request))
        while self.response is None:
            self.connection.process_data_events(10)
        return self.response
