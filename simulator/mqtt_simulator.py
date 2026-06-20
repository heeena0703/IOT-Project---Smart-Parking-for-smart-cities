"""
Simple MQTT simulator that publishes occupancy messages for parking spots.
By default it publishes to topic `parking/spot/<id>` with payload JSON: {"id": "1", "occupied": true}

Requires: paho-mqtt

Usage:
  python simulator/mqtt_simulator.py --broker localhost --port 1883 --interval 1

"""
import argparse
import json
import random
import time
import threading

import paho.mqtt.client as mqtt


def run(broker, port, num_spots, interval, topic_prefix):
    client = mqtt.Client()
    client.connect(broker, port)

    def loop():
        while True:
            sid = str(random.randint(1, num_spots))
            occupied = random.choice([True, False])
            payload = json.dumps({"id": sid, "occupied": occupied})
            topic = f"{topic_prefix}/{sid}"
            client.publish(topic, payload)
            print(f"Published to {topic}: {payload}")
            time.sleep(interval)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping simulator')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--broker', default='localhost')
    p.add_argument('--port', type=int, default=1883)
    p.add_argument('--num-spots', type=int, default=5)
    p.add_argument('--interval', type=float, default=2.0)
    p.add_argument('--topic-prefix', default='parking/spot')
    args = p.parse_args()
    run(args.broker, args.port, args.num_spots, args.interval, args.topic_prefix)
