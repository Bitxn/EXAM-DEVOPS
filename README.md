# devops-ques4 — Hospital Patient Record API (minimal)

Synthetic data only. Flask REST API, containerized, deployed on Minikube.

## API
- `POST /patients`  → add `{name, age, ...}` (missing name/age → 400)
- `GET /patients`   → list all
- `GET /patients/<id>` → one (missing → 404)

## Run locally
```bash
pip install flask
python app.py
curl -X POST http://localhost:5000/patients -H "Content-Type: application/json" -d '{"name":"Asha","age":30}'
curl http://localhost:5000/patients
```

## Run on Minikube
```bash
eval $(minikube docker-env)
docker build -t flask-api:latest .
kubectl apply -f k8s.yaml
minikube service flask-svc --url
```
