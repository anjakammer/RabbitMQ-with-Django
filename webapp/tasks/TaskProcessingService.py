import pika, uuid, time, json, os, logging, sys
from django.dispatch import Signal

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TaskProcessingService():
    QUEUE_BROKER = os.getenv('QUEUE_BROKER')
    QUEUE_NAME = os.getenv('QUEUE_NAME')

    task_finished = Signal(providing_args=["response"])
    task_processing = Signal(providing_args=["id"])

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
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.QUEUE_BROKER))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.__on_response, no_ack=False,
                                   queue=self.callback_queue)
        self.channel.confirm_delivery()

    def __on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

            response_string = body.decode('unicode_escape')
            response_object = json.loads(response_string)

            logging.debug('received %s', response_object)
            self.task_finished.send(sender=self.__class__, response=response_object)

    def send(self, request, task_id, task_type):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        logging.info('[x] Requesting %s for %s', task_type, request)
        request_confirmed = self.channel.basic_publish(exchange='',
                                                       routing_key=task_type + '_' + self.QUEUE_NAME,
                                                       properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                       delivery_mode=2,  # make message persistent
                                       content_type='application/json',
                                                       ),
                                                       body=json.dumps(request))

        if request_confirmed:
            self.task_processing.send(sender=self.__class__, id=task_id)
            while self.response is None:
                self.connection.process_data_events(10)
        else:
            logging.warning('%s Request with id %d could not be confirmed', task_type, task_id)
