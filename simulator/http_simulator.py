"""
Simple HTTP simulator that POSTs occupancy JSON to the Flask `/api/sensor` endpoint.

Usage:
  python simulator/http_simulator.py --url http://localhost:5000/api/sensor --interval 1

"""
import argparse
import json
import random
import time
import requests


def run(url, num_spots, interval):
    try:
        while True:
            sid = str(random.randint(1, num_spots))
            occupied = random.choice([True, False])
            payload = {"id": sid, "occupied": occupied}
            r = requests.post(url, json=payload)
            print(r.status_code, r.text)
            time.sleep(interval)
    except KeyboardInterrupt:
        print('Stopping HTTP simulator')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://localhost:5000/api/sensor')
    p.add_argument('--num-spots', type=int, default=5)
    p.add_argument('--interval', type=float, default=1.0)
    args = p.parse_args()
    run(args.url, args.num_spots, args.interval)
