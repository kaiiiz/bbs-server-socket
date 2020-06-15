KAFKA_SERVER = "ec2-3-233-220-168.compute-1.amazonaws.com"
KAFKA_PORT = 9092

from kafka import KafkaConsumer
import json
import threading

class Pull(threading.Thread):
    def __init__(self, consumer):
        super().__init__()
        self.consumer = consumer

    def run(self):
        while True:
            message = self.consumer.poll(timeout_ms=1000)
            for topic_partition, records in message.items():
                print(topic)
                for r in records:
                    print(r.value)

    def change(self, consumer):
        print("change")
        self.consumer = consumer


def new_consumer(sub):
    consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')),
                            bootstrap_servers=[f"{KAFKA_SERVER}:{KAFKA_PORT}"])
    if sub is not None:
        consumer.subscribe((sub,))
    return consumer

consumer = new_consumer(None)
p = Pull(consumer)
p.start()

while True:
    b = input()
    consumer = new_consumer(b)
    p.consumer = consumer
    print(consumer.subscription())
    if b == "u":
        print("unsubscribe")
        consumer.unsubscribe()
        print(consumer.subscription())

