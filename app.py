import os, sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
PG = os.getenv("DB_HOST")

def conn():
    if PG:
        import psycopg2
        return psycopg2.connect(host=PG, dbname="hospital", user="app",
                                password=os.getenv("DB_PASSWORD", "secret")), "%s"
    return sqlite3.connect("patients.db"), "?"

def init():
    c, _ = conn()
    cur = c.cursor()
    pk = "SERIAL PRIMARY KEY" if PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cur.execute(f"CREATE TABLE IF NOT EXISTS patients (id {pk}, name TEXT, age INT, ailment TEXT)")
    c.commit(); c.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/patients")
def add():
    d = request.get_json(silent=True)
    if not d or not {"name", "age", "ailment"} <= d.keys():
        return jsonify(error="invalid"), 400
    if not isinstance(d["age"], int) or d["age"] < 0:
        return jsonify(error="bad age"), 400
    c, ph = conn(); cur = c.cursor()
    cur.execute(f"INSERT INTO patients (name, age, ailment) VALUES ({ph}, {ph}, {ph})",
                (d["name"], d["age"], d["ailment"]))
    if PG:
        cur.execute("SELECT lastval()"); pid = cur.fetchone()[0]
    else:
        pid = cur.lastrowid
    c.commit(); c.close()
    return jsonify(id=pid, name=d["name"], age=d["age"], ailment=d["ailment"]), 201

@app.get("/patients/<int:pid>")
def get(pid):
    c, ph = conn(); cur = c.cursor()
    cur.execute(f"SELECT id, name, age, ailment FROM patients WHERE id = {ph}", (pid,))
    r = cur.fetchone(); c.close()
    if not r:
        return jsonify(error="not found"), 404
    return jsonify(id=r[0], name=r[1], age=r[2], ailment=r[3])

@app.get("/patients")
def all_patients():
    c, _ = conn(); cur = c.cursor()
    cur.execute("SELECT id, name, age, ailment FROM patients")
    rows = cur.fetchall(); c.close()
    return jsonify([{"id": r[0], "name": r[1], "age": r[2], "ailment": r[3]} for r in rows])

if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000)
