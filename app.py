from flask import Flask, request, jsonify

app = Flask(__name__)
patients = []

@app.post("/patients")
def add():
    d = request.get_json(silent=True)
    if not d or "name" not in d or "age" not in d:
        return jsonify(error="invalid"), 400
    d["id"] = len(patients) + 1
    patients.append(d)
    return jsonify(d), 201

@app.get("/patients")
def all_patients():
    return jsonify(patients)

@app.get("/patients/<int:pid>")
def get(pid):
    for p in patients:
        if p["id"] == pid:
            return jsonify(p)
    return jsonify(error="not found"), 404



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


