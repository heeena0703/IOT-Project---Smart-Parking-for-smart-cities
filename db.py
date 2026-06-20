import sqlite3
from contextlib import closing
from pathlib import Path


SCHEMA = '''
CREATE TABLE IF NOT EXISTS spots (
  id TEXT PRIMARY KEY,
  occupied INTEGER NOT NULL
);
'''


def init_db(db_path: str, num_spots: int = 5):
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    with closing(con):
        cur = con.cursor()
        cur.executescript(SCHEMA)
        # initialize spots if not present
        for i in range(1, num_spots + 1):
            sid = str(i)
            cur.execute('INSERT OR IGNORE INTO spots(id, occupied) VALUES(?, ?)', (sid, 0))
        con.commit()


def get_all_spots(db_path: str):
    con = sqlite3.connect(db_path)
    with closing(con):
        cur = con.cursor()
        cur.execute('SELECT id, occupied FROM spots ORDER BY id ASC')
        rows = cur.fetchall()
        return [{"id": r[0], "occupied": bool(r[1])} for r in rows]


def get_spot(db_path: str, spot_id: str):
    con = sqlite3.connect(db_path)
    with closing(con):
        cur = con.cursor()
        cur.execute('SELECT id, occupied FROM spots WHERE id = ?', (spot_id,))
        r = cur.fetchone()
        if not r:
            return None
        return {"id": r[0], "occupied": bool(r[1])}


def set_spot(db_path: str, spot_id: str, occupied: bool):
    con = sqlite3.connect(db_path)
    with closing(con):
        cur = con.cursor()
        cur.execute('UPDATE spots SET occupied = ? WHERE id = ?', (1 if occupied else 0, spot_id))
        con.commit()
        return get_spot(db_path, spot_id)
