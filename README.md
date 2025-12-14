# Kubernetes Uptime Monitor Lab (FastAPI + Worker + Redis)

## Features
- FastAPI API to add/list/delete monitored URLs
- Worker checks URLs periodically (status + latency)
- Redis storage (simple MVP)
- Kubernetes manifests: Namespace, Deployments, Services, ConfigMap, Secret, liveness/readiness probes
- Prometheus metrics endpoints:
  - API: /metrics
  - Worker: :9102/metrics

## Local run (Docker Compose)
```bash
make compose-up
curl -X POST localhost:8000/monitors -H "content-type: application/json" \
  -d '{"url":"https://example.com","interval_seconds":30,"tags":["demo"]}'
curl localhost:8000/monitors
