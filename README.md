# devops-ques4 — Hospital Patient Record API (Secure Deployment)

Synthetic data only. Flask REST API + Postgres, on Docker and Minikube, with AppArmor.

## API
| Method | Path | Result |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |
| POST | `/patients` | add (JSON: name, age, ailment) → `201`; invalid → `400` |
| GET | `/patients/<id>` | get one → `200`; missing → `404` |
| GET | `/patients` | list all |

## 1. Run with Docker (custom bridge, DB port NOT published)
```bash
docker compose up --build -d
```
Only port 5000 is exposed; Postgres stays on the internal `hospital-net` bridge.

Verify DB reachable by container name:
```bash
docker compose exec flask-api sh -c "getent hosts db"
```

Test:
```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/patients -H "Content-Type: application/json" -d '{"name":"Asha","age":30,"ailment":"fever"}'
curl http://localhost:5000/patients/1
curl -X POST http://localhost:5000/patients -H "Content-Type: application/json" -d '{"name":"x"}'   # 400
curl http://localhost:5000/patients/999   # 404
curl http://localhost:5432                 # refused: DB not published
```

## 2. Run on Minikube
```bash
eval $(minikube docker-env)
docker build -t flask-api:latest .
kubectl apply -f k8s/k8s.yaml
kubectl get pods
minikube service flask-svc --url
```
`db` Service is ClusterIP (internal); `flask-svc` is NodePort (reachable).

## 3. AppArmor (Linux / WSL2 only)
```bash
sudo apparmor_parser -r apparmor/hospital-flask
docker run -d --name flask-api --network hospital-net \
  --security-opt apparmor=hospital-flask -e DB_HOST=db -p 5000:5000 flask-api:latest

docker exec -it flask-api sh -c 'echo hi > /tmp/ok && echo ALLOWED'   # works
docker exec -it flask-api sh -c 'echo x  > /etc/passwd'               # Permission denied
```

## 4. Diagnose a failure from logs
Break it (e.g. set `DB_HOST=wrong`), then:
```bash
docker compose logs flask-api        # shows host resolution error
kubectl logs deploy/flask-api
kubectl describe pod <pod>
```

## Cleanup
```bash
docker compose down -v
kubectl delete -f k8s/k8s.yaml
```
