import pika

credentials = pika.PlainCredentials('pi2ricc','ricc')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='hello')


channel.basic_publish(
    exchange='',
    routing_key='hello',
    body="Hello World!"
)

print("[x] Sent 'Hello World!'")

connection.close()