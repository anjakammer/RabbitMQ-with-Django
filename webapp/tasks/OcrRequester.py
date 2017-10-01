import pika, uuid, time, json, os
from django.dispatch import Signal

class OcrRequester():
    QUEUE_BROKER = os.getenv('QUEUE_BROKER')
    QUEUE_NAME = os.getenv('OCR_QUEUE_NAME')

    ocr_finished = Signal(providing_args=["id", "result"])

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

            response_string = body.decode('unicode_escape')
            dataform = response_string.strip("'<>() ").replace('\'', '\"')
            response_object = json.loads(dataform)

            id = response_object.get('id')
            result = response_object.get('result')

            print('received %s' % response_object)
            self.ocr_finished.send(sender=self.__class__, id=id, result=result)

    def send(self, ocr_request):
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
