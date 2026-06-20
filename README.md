# IOT-Project---Smart-Parking-for-smart-cities

IOT project

This repository now contains a small Flask prototype (backend + static dashboard) to simulate a smart parking system locally.

Quick start (Windows PowerShell):

1. Create a virtual environment and activate it

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

3. Run the app

```powershell
python app.py
```

Open http://localhost:5000 in your browser to see the dashboard.

4. Run tests

```powershell
python -m pytest -q
```

Files added:

- `app.py` – Flask application (API + static file serving)
- `static/index.html`, `static/app.js` – simple dashboard and controls
- `tests/test_api.py` – pytest tests for the API
- `requirements.txt` – pinned dependencies for quick setup

If you want additional features (persistence, MQTT sensor simulation, Dockerfile), tell me which one to add next.
Node-RED + Mosquitto (local integration)

---

The repository includes a `docker-compose.nodered.yml` which runs Node-RED and a Mosquitto broker locally. Node-RED can subscribe to `parking/spot/+` topics and forward the sensor payloads to the Flask API.

Run Node-RED and Mosquitto:

```powershell
docker compose -f docker-compose.nodered.yml up -d
```

Open Node-RED editor at http://localhost:1880, import `nodered_flow.json` via the menu (Import -> Clipboard -> paste file contents). The flow includes an MQTT in node and an HTTP request node that forwards messages to `http://host.docker.internal:5000/api/sensor` (this resolves to your host machine when running in Docker Desktop).

Use the HTTP simulator or MQTT simulator to publish messages and watch Node-RED forward them to your Flask app and update the UI.

```
# IOT-Project---Smart-Parking-for-smart-cities
IOT project
```
