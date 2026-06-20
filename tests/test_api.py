import json

from app import create_app
import os
import tempfile
from db import init_db, get_spot


def test_get_spots():
    app = create_app()
    client = app.test_client()
    r = client.get('/api/spots')
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_reserve_and_release():
    app = create_app()
    client = app.test_client()

    # reserve spot 1
    r = client.post('/api/spots/1/reserve')
    assert r.status_code == 200
    assert r.get_json()['occupied'] is True

    # reserving again should fail
    r = client.post('/api/spots/1/reserve')
    assert r.status_code == 400

    # release
    r = client.post('/api/spots/1/release')
    assert r.status_code == 200
    assert r.get_json()['occupied'] is False

    # releasing again should fail
    r = client.post('/api/spots/1/release')
    assert r.status_code == 400


def test_sensor_endpoint():
    app = create_app()
    client = app.test_client()

    r = client.post('/api/sensor', data=json.dumps({'id': '2', 'occupied': True}), content_type='application/json')
    assert r.status_code == 200
    assert r.get_json()['occupied'] is True


def test_persistence_with_sqlite(tmp_path):
    # create a temp sqlite file
    db_file = tmp_path / 'test.db'
    db_path = str(db_file)

    # initialize DB and create app configured for DB
    os.environ['DB_PATH'] = db_path
    app1 = create_app()
    client1 = app1.test_client()

    # reserve spot 3
    r = client1.post('/api/spots/3/reserve')
    assert r.status_code == 200
    assert r.get_json()['occupied'] is True

    # recreate app (simulates restart) and verify spot 3 is still occupied
    app2 = create_app()
    client2 = app2.test_client()
    r2 = client2.get('/api/spots')
    spots = r2.get_json()
    s3 = next((s for s in spots if s['id'] == '3'), None)
    assert s3 is not None and s3['occupied'] is True

    # cleanup env
    del os.environ['DB_PATH']
