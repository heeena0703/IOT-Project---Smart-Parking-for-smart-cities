import requests
import time

url = 'http://localhost:5000/api/events'
print('Connecting to', url)
try:
    r = requests.get(url, stream=True, timeout=5)
except Exception as e:
    print('connect error', e)
    raise SystemExit(1)

start = time.time()
count = 0
try:
    for raw in r.iter_lines():
        if raw:
            line = raw.decode()
            print('LINE>', line)
            if line.startswith('data:'):
                data = line[5:].strip()
                print('EVENT data:', data)
                count += 1
        if time.time() - start > 12 or count >= 5:
            break
finally:
    try:
        r.close()
    except Exception:
        pass

print('done')
