.PHONY: compose-up compose-down k8s-apply k8s-delete k8s-status port-forward

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down -v

# For OrbStack: Docker images must be available locally for the Kubernetes cluster.
# Build images locally before applying Kubernetes manifests.
build-images:
	docker build -t uptime-api:local -f app/Dockerfile.api .
	docker build -t uptime-worker:local -f app/Dockerfile.worker .

k8s-apply: build-images
	kubectl apply -f deploy/k8s/00-namespace.yaml
	kubectl apply -f deploy/k8s/01-configmap.yaml
	kubectl apply -f deploy/k8s/02-secret.yaml
	kubectl apply -f deploy/k8s/03-redis-deployment.yaml
	kubectl apply -f deploy/k8s/04-redis-service.yaml
	kubectl apply -f deploy/k8s/05-api-deployment.yaml
	kubectl apply -f deploy/k8s/06-api-service.yaml
	kubectl apply -f deploy/k8s/07-worker-deployment.yaml

k8s-delete:
	kubectl delete ns uptime --ignore-not-found=true

k8s-status:
	kubectl get all -n uptime

port-forward:
	kubectl -n uptime port-forward svc/api 8000:80

ingress-forward:
	kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
