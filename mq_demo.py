import os

import logzero
import pika
from logzero import logger

from qingdian_jian.settings import RABBITMQ_HOSTS, RABBITMQ_PASSWORD, RABBITMQ_POST, RABBITMQ_USER

current_module = os.path.splitext(os.path.basename(__file__))[0]

logzero.logfile(f"/tmp/{current_module}.log", maxBytes=30_000_000, backupCount=3, encoding='utf-8')


def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOSTS, RABBITMQ_POST, '/', credentials))
    channel = connection.channel()
    channel.queue_declare(queue='pipeline', durable=True)
    channel.basic_consume(callback, queue='pipeline', no_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def callback(ch, method, properties, body):
    logger.info("[x] Received %r" % body)
    logger.info(body.decode('utf-8'))


def send_mssage(msg):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOSTS, RABBITMQ_POST, '/', credentials))
    channel = connection.channel()

    # 声明queue
    channel.queue_declare(queue='pipeline', durable=True)
    # print(type(mysql_format))

    # print(mysql_format_json)
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange='',
                          routing_key='pipeline',
                          body=msg)
    logger.info("Sent success!!")


if __name__ == '__main__':
    send_mssage('hello girl')
    main()
