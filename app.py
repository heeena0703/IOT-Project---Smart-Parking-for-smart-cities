import os
import json
import queue
from flask import Flask, jsonify, request, abort, Response, stream_with_context

from db import init_db, get_all_spots, get_spot, set_spot


def create_app():
    app = Flask(__name__, static_folder='static')

    # Optional DB persistence
    db_path = os.environ.get('DB_PATH')
    if db_path:
        # initialize DB and use it as source of truth
        init_db(db_path, num_spots=5)
        app.config['DB_PATH'] = db_path
    else:
        # In-memory parking spots (id: {id, occupied})
        spots = {str(i): {"id": str(i), "occupied": False} for i in range(1, 6)}
        app.config['SPOTS'] = spots

    # event queues for SSE clients
    app.config['EVENT_QUEUES'] = []

    def publish_event(event: dict):
        # push event (dict) to all client queues (non-blocking)
        dead = []
        for q in list(app.config['EVENT_QUEUES']):
            try:
                q.put_nowait(event)
            except Exception:
                dead.append(q)
        for q in dead:
            try:
                app.config['EVENT_QUEUES'].remove(q)
            except ValueError:
                pass

    @app.route('/api/events')
    def events():
        def gen(q):
            try:
                while True:
                    item = q.get()
                    yield f"data: {json.dumps(item)}\n\n"
            finally:
                # remove queue when client disconnects
                try:
                    app.config['EVENT_QUEUES'].remove(q)
                except Exception:
                    pass

        q = queue.Queue()
        app.config['EVENT_QUEUES'].append(q)
        return Response(stream_with_context(gen(q)), mimetype='text/event-stream')

    @app.route('/api/spots', methods=['GET'])
    def get_spots():
        if app.config.get('DB_PATH'):
            return jsonify(get_all_spots(app.config['DB_PATH']))
        return jsonify(list(app.config['SPOTS'].values()))

    def get_spot_or_404(spot_id):
        if app.config.get('DB_PATH'):
            spot = get_spot(app.config['DB_PATH'], spot_id)
            if not spot:
                abort(404, description='Spot not found')
            return spot
        if spot_id not in app.config['SPOTS']:
            abort(404, description='Spot not found')
        return app.config['SPOTS'][spot_id]

    @app.route('/api/spots/<spot_id>/reserve', methods=['POST'])
    def reserve(spot_id):
        spot = get_spot_or_404(spot_id)
        if spot['occupied']:
            return jsonify({"error": "already occupied"}), 400
        if app.config.get('DB_PATH'):
            updated = set_spot(app.config['DB_PATH'], spot_id, True)
            publish_event({"type": "update", "spot": updated})
            return jsonify(updated)
        spot['occupied'] = True
        publish_event({"type": "update", "spot": spot})
        return jsonify(spot)

    @app.route('/api/spots/<spot_id>/release', methods=['POST'])
    def release(spot_id):
        spot = get_spot_or_404(spot_id)
        if app.config.get('DB_PATH'):
            # check current state
            current = get_spot(app.config['DB_PATH'], spot_id)
            if not current['occupied']:
                return jsonify({"error": "already free"}), 400
            updated = set_spot(app.config['DB_PATH'], spot_id, False)
            publish_event({"type": "update", "spot": updated})
            return jsonify(updated)
        if not spot['occupied']:
            return jsonify({"error": "already free"}), 400
        spot['occupied'] = False
        publish_event({"type": "update", "spot": spot})
        return jsonify(spot)

    @app.route('/api/sensor', methods=['POST'])
    def sensor():
        data = request.get_json() or {}
        sid = str(data.get('id'))
        occupied = bool(data.get('occupied'))
        if app.config.get('DB_PATH'):
            # ensure spot exists
            sp = get_spot(app.config['DB_PATH'], sid)
            if not sp:
                abort(404, description='Spot not found')
            updated = set_spot(app.config['DB_PATH'], sid, occupied)
            publish_event({"type": "update", "spot": updated})
            return jsonify(updated)
        if sid not in app.config['SPOTS']:
            abort(404, description='Spot not found')
        app.config['SPOTS'][sid]['occupied'] = occupied
        publish_event({"type": "update", "spot": app.config['SPOTS'][sid]})
        return jsonify(app.config['SPOTS'][sid])

    @app.route('/', methods=['GET'])
    def index():
        return app.send_static_file('index.html')

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5000, debug=True)
