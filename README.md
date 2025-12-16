# Kubernetes Uptime Monitor Lab

A production-like Kubernetes project demonstrating how to build, run and operate
a small service using common DevOps patterns.

The system allows you to register URLs, periodically checks their availability
(HTTP status and latency), and exposes the results via a REST API.

---

## Architecture

```
Client
  ↓
Ingress (nginx)
  ↓
API (FastAPI)
  ↓             ↑
Redis ← Worker
```

- **API** – REST service for managing monitored URLs
- **Worker** – background process that periodically checks URLs
- **Redis** – shared storage between API and worker

---

## Features

- FastAPI REST API
- Background worker for periodic uptime checks
- Redis as shared storage
- Local development with Docker Compose
- Kubernetes deployment:
  - Namespace
  - Deployments (API, Worker, Redis)
  - Services (ClusterIP)
  - ConfigMap & Secret
  - Liveness and readiness probes
  - Ingress (nginx)
  - Horizontal Pod Autoscaler (CPU-based)
- Health endpoints:
  - `/healthz`
  - `/readyz`

---

## Local development (Docker Compose)

Run the full system locally:

```bash
make compose-up
```

Create a monitor:

```bash
curl -X POST localhost:8000/monitors \
  -H "content-type: application/json" \
  -d '{"url":"https://example.com","interval_seconds":30,"tags":["demo"]}'
```

Check the result:

```bash
curl localhost:8000/monitors/<ID>
```

---

## Kubernetes deployment

Deploy to a local Kubernetes cluster (tested with OrbStack):

```bash
kubectl apply -f deploy/k8s
```

Check resources:

```bash
kubectl get pods -n uptime
kubectl get svc -n uptime
kubectl get ingress -n uptime
```

---

## Access via Ingress

The API is exposed via nginx ingress:

```
http://uptime.local
```

For local clusters, access can be tested using port-forward:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8081:80
```

Then open:

```
http://uptime.local:8081/docs
```

---

## Autoscaling (HPA)

The API deployment includes a CPU-based Horizontal Pod Autoscaler configuration.

> Note:
> On local Kubernetes clusters (OrbStack / k3s), pod-level metrics may be limited.
> The HPA configuration is production-ready and works as expected on managed
> Kubernetes services such as EKS, GKE or AKS.

---

## Notes

- This project focuses on Kubernetes and DevOps practices rather than application complexity.
- Monitoring and observability (Prometheus / Grafana) are demonstrated in a separate repository.

---

## Why this project

This project was built to demonstrate:
- containerized application design
- Kubernetes fundamentals
- ingress routing
- health checks and readiness
- autoscaling concepts
- realistic local-to-Kubernetes workflow
