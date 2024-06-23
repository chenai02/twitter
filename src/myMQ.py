import pika
import json
from datetime import datetime
import time
from loguru import logger


class MessageBody:
    def __init__(self, msg_type, title, content, QKey, links=None, create_time=None):
        self.type = msg_type
        self.title = title
        self.content = content
        self.links = links
        self.create_time = create_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.QKey = QKey

    def to_json(self):
        # 使用字典推导式来过滤掉值为None的属性
        data = {key: value for key, value in self.__dict__.items() if value is not None}
        return json.dumps(data, ensure_ascii=False, indent=4)

class RabbitMQProducer:
    def __init__(self, host, port, username, password, retry_count):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.retry_count = retry_count
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        retries = 0
        while retries < self.retry_count:
            try:
                user_info = pika.PlainCredentials(self.username, self.password)
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, '/', user_info))
                self.channel = self.connection.channel()
                return
            except Exception as e:
                retries += 1
                time.sleep(2)  # 等待2秒后重试
        logger.error("Failed to connect to RabbitMQ, this message is skipped")
        self.connection = None
        self.channel = None

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def publish_message(self, queue_name, message):
        if not self.channel or self.connection.is_closed or self.channel.is_closed:
            self.connect()

        if not self.channel:
            logger.error("Failed to publish message")
            return
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        except Exception as e:
            self.connect()  # Try to reconnect if publish fails
            if self.channel:
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
            else:
                logger.error(f"Failed to publish message:{e}")


    def consume_messages(self, queue_name, callback):
        if not self.channel or self.connection.is_closed or self.channel.is_closed:
            self.connect()

        if not self.channel:
            raise ("Failed to start consuming: no connection to RabbitMQ")
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming() # 直接阻塞，除非自己实现异步代码

def consumer_callback(ch, method, properties, body):
    json_str = body.decode('utf-8')
    json_dict = json.loads(json_str)
    print('消费者收到:{}'.format(json_dict), type(json_dict))
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    myMQ = RabbitMQProducer('120.24.193.184', 5672, 'rain','rain@123', 5)
    # myMQ.consume_messages('rain_mq', consumer_callback)
    while True:
        try:
            current_time = datetime.now()
            message_body = MessageBody(
                msg_type=3,
                title='test1',
                content='test1',
                links=['xxxxx'],
                create_time=current_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            myMQ.publish_message('rain_mq', message_body.to_json())
            time.sleep(5)
        except Exception as e:
            myMQ.close_connection()
            logger.error(f"MQ connect is Failed, please check:{e}")