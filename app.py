import os, time, psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname="hospital",
        user="app",
        password=os.getenv("DB_PASSWORD", "secret"),
    )

def init():
    for _ in range(15):
        try:
            c = db(); cur = c.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS patients (id SERIAL PRIMARY KEY, name TEXT, age INT, ailment TEXT)")
            c.commit(); cur.close(); c.close()
            return
        except Exception:
            time.sleep(2)

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
    c = db(); cur = c.cursor()
    cur.execute("INSERT INTO patients (name, age, ailment) VALUES (%s,%s,%s) RETURNING id",
                (d["name"], d["age"], d["ailment"]))
    pid = cur.fetchone()[0]; c.commit(); cur.close(); c.close()
    return jsonify(id=pid, name=d["name"], age=d["age"], ailment=d["ailment"]), 201

@app.get("/patients/<int:pid>")
def get(pid):
    c = db(); cur = c.cursor()
    cur.execute("SELECT id, name, age, ailment FROM patients WHERE id=%s", (pid,))
    r = cur.fetchone(); cur.close(); c.close()
    if not r:
        return jsonify(error="not found"), 404
    return jsonify(id=r[0], name=r[1], age=r[2], ailment=r[3])

@app.get("/patients")
def all_patients():
    c = db(); cur = c.cursor()
    cur.execute("SELECT id, name, age, ailment FROM patients")
    rows = cur.fetchall(); cur.close(); c.close()
    return jsonify([{"id": r[0], "name": r[1], "age": r[2], "ailment": r[3]} for r in rows])

if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000)
