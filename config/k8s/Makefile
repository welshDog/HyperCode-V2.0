# HyperCode Kubernetes Deployment Makefile

# Configuration
NAMESPACE := hypercode
REGISTRY := your-registry.com/hypercode
VERSION := latest

# Kubectl context (change if needed)
CONTEXT := $(shell kubectl config current-context)

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: check-context
check-context: ## Verify kubectl context
	@echo "Current context: $(CONTEXT)"
	@echo "Namespace: $(NAMESPACE)"
	@read -p "Is this correct? [y/N] " -n 1 -r; \
	echo; \
	if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Aborted."; \
		exit 1; \
	fi

.PHONY: build-all
build-all: ## Build all Docker images
	@echo "Building all images..."
	docker build -t $(REGISTRY)/hypercode-core:$(VERSION) ./HyperCode-V2.0/THE\ HYPERCODE/hypercode-core
	docker build -t $(REGISTRY)/crew-orchestrator:$(VERSION) ./agents/crew-orchestrator
	@for agent in 01-frontend-specialist 02-backend-specialist 03-database-architect 04-qa-engineer 05-devops-engineer 06-security-engineer 07-system-architect 08-project-strategist; do \
		echo "Building $$agent..."; \
		docker build -t $(REGISTRY)/$$agent:$(VERSION) ./agents/$$agent; \
	done

.PHONY: push-all
push-all: ## Push all Docker images to registry
	@echo "Pushing all images..."
	docker push $(REGISTRY)/hypercode-core:$(VERSION)
	docker push $(REGISTRY)/crew-orchestrator:$(VERSION)
	@for agent in 01-frontend-specialist 02-backend-specialist 03-database-architect 04-qa-engineer 05-devops-engineer 06-security-engineer 07-system-architect 08-project-strategist; do \
		echo "Pushing $$agent..."; \
		docker push $(REGISTRY)/$$agent:$(VERSION); \
	done

.PHONY: create-namespace
create-namespace: ## Create namespace
	kubectl apply -f k8s/00-namespace.yaml

.PHONY: create-secrets
create-secrets: ## Create secrets (interactive)
	@echo "Creating secrets..."
	@echo "Enter Anthropic API Key:"; read ANTHROPIC_KEY; \
	JWT_SECRET=$$(openssl rand -base64 32); \
	POSTGRES_PASS=$$(openssl rand -base64 24); \
	REDIS_PASS=$$(openssl rand -base64 24); \
	GRAFANA_PASS=$$(openssl rand -base64 16); \
	kubectl create secret generic hypercode-secrets \
		--from-literal=anthropic-api-key="$$ANTHROPIC_KEY" \
		--from-literal=hypercode-jwt-secret="$$JWT_SECRET" \
		--from-literal=postgres-password="$$POSTGRES_PASS" \
		--from-literal=redis-password="$$REDIS_PASS" \
		--from-literal=grafana-admin-password="$$GRAFANA_PASS" \
		-n $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

.PHONY: deploy-infra
deploy-infra: ## Deploy infrastructure (Redis, Postgres)
	kubectl apply -f k8s/02-configmap.yaml
	kubectl apply -f k8s/03-persistent-volumes.yaml
	kubectl apply -f k8s/04-redis.yaml
	kubectl apply -f k8s/05-postgres.yaml
	@echo "Waiting for infrastructure to be ready..."
	kubectl wait --for=condition=ready pod -l app=redis -n $(NAMESPACE) --timeout=180s
	kubectl wait --for=condition=ready pod -l app=postgres -n $(NAMESPACE) --timeout=180s

.PHONY: deploy-core
deploy-core: ## Deploy core services
	kubectl apply -f k8s/06-hypercode-core.yaml
	kubectl apply -f k8s/07-crew-orchestrator.yaml
	@echo "Waiting for core services..."
	kubectl wait --for=condition=available deployment/hypercode-core -n $(NAMESPACE) --timeout=180s

.PHONY: deploy-agents
deploy-agents: ## Deploy all agents
	kubectl apply -f k8s/08-agents.yaml
	@echo "Agents deployed"

.PHONY: deploy-dashboard
deploy-dashboard: ## Deploy dashboard
	kubectl apply -f k8s/09-dashboard.yaml

.PHONY: deploy-monitoring
deploy-monitoring: ## Deploy monitoring stack
	kubectl apply -f k8s/11-monitoring.yaml

.PHONY: deploy-network-policies
deploy-network-policies: ## Apply network policies
	kubectl apply -f k8s/13-network-policy.yaml

.PHONY: deploy-ingress
deploy-ingress: ## Deploy ingress
	kubectl apply -f k8s/12-ingress.yaml

.PHONY: deploy-hpa
deploy-hpa: ## Deploy horizontal pod autoscalers
	kubectl apply -f k8s/14-hpa.yaml

.PHONY: deploy-all
deploy-all: check-context create-namespace create-secrets deploy-infra deploy-core deploy-agents deploy-dashboard deploy-monitoring deploy-network-policies deploy-ingress deploy-hpa ## Deploy everything
	@echo "Deployment complete!"
	@echo "Run 'make status' to check deployment status"

.PHONY: status
status: ## Show deployment status
	@echo "=== Namespace ==="
	kubectl get namespace $(NAMESPACE)
	@echo "\n=== Pods ==="
	kubectl get pods -n $(NAMESPACE)
	@echo "\n=== Services ==="
	kubectl get svc -n $(NAMESPACE)
	@echo "\n=== Deployments ==="
	kubectl get deployments -n $(NAMESPACE)
	@echo "\n=== StatefulSets ==="
	kubectl get statefulsets -n $(NAMESPACE)
	@echo "\n=== PVCs ==="
	kubectl get pvc -n $(NAMESPACE)
	@echo "\n=== Ingress ==="
	kubectl get ingress -n $(NAMESPACE)

.PHONY: logs-core
logs-core: ## Show HyperCode Core logs
	kubectl logs -f deployment/hypercode-core -n $(NAMESPACE)

.PHONY: logs-orchestrator
logs-orchestrator: ## Show Crew Orchestrator logs
	kubectl logs -f deployment/crew-orchestrator -n $(NAMESPACE)

.PHONY: port-forward-core
port-forward-core: ## Port forward HyperCode Core
	kubectl port-forward svc/hypercode-core 8000:8000 -n $(NAMESPACE)

.PHONY: port-forward-dashboard
port-forward-dashboard: ## Port forward Dashboard
	kubectl port-forward svc/dashboard 8088:80 -n $(NAMESPACE)

.PHONY: port-forward-grafana
port-forward-grafana: ## Port forward Grafana
	kubectl port-forward svc/grafana 3001:3000 -n $(NAMESPACE)

.PHONY: port-forward-prometheus
port-forward-prometheus: ## Port forward Prometheus
	kubectl port-forward svc/prometheus 9090:9090 -n $(NAMESPACE)

.PHONY: backup-postgres
backup-postgres: ## Backup Postgres database
	@mkdir -p backups
	kubectl exec -it postgres-0 -n $(NAMESPACE) -- pg_dump -U postgres hypercode > backups/postgres-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Backup created in backups/ directory"

.PHONY: restore-postgres
restore-postgres: ## Restore Postgres database (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore-postgres BACKUP_FILE=backups/postgres-20240101-120000.sql"; \
		exit 1; \
	fi
	kubectl exec -i postgres-0 -n $(NAMESPACE) -- psql -U postgres hypercode < $(BACKUP_FILE)

.PHONY: scale-core
scale-core: ## Scale HyperCode Core (requires REPLICAS variable)
	@if [ -z "$(REPLICAS)" ]; then \
		echo "Error: REPLICAS not specified"; \
		echo "Usage: make scale-core REPLICAS=5"; \
		exit 1; \
	fi
	kubectl scale deployment hypercode-core --replicas=$(REPLICAS) -n $(NAMESPACE)

.PHONY: restart-core
restart-core: ## Restart HyperCode Core
	kubectl rollout restart deployment/hypercode-core -n $(NAMESPACE)

.PHONY: restart-agents
restart-agents: ## Restart all agents
	@for agent in frontend-specialist backend-specialist database-architect qa-engineer devops-engineer security-engineer system-architect project-strategist; do \
		echo "Restarting $$agent..."; \
		kubectl rollout restart deployment/$$agent -n $(NAMESPACE); \
	done

.PHONY: update-image-core
update-image-core: ## Update HyperCode Core image
	kubectl set image deployment/hypercode-core hypercode-core=$(REGISTRY)/hypercode-core:$(VERSION) -n $(NAMESPACE)
	kubectl rollout status deployment/hypercode-core -n $(NAMESPACE)

.PHONY: rollback-core
rollback-core: ## Rollback HyperCode Core deployment
	kubectl rollout undo deployment/hypercode-core -n $(NAMESPACE)

.PHONY: shell-core
shell-core: ## Get shell in HyperCode Core pod
	kubectl exec -it deployment/hypercode-core -n $(NAMESPACE) -- /bin/sh

.PHONY: shell-postgres
shell-postgres: ## Get psql shell in Postgres
	kubectl exec -it postgres-0 -n $(NAMESPACE) -- psql -U postgres hypercode

.PHONY: shell-redis
shell-redis: ## Get redis-cli shell in Redis
	kubectl exec -it redis-0 -n $(NAMESPACE) -- redis-cli

.PHONY: top
top: ## Show resource usage
	kubectl top pods -n $(NAMESPACE)
	@echo "\n=== Node usage ==="
	kubectl top nodes

.PHONY: events
events: ## Show recent events
	kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

.PHONY: describe-pod
describe-pod: ## Describe a pod (requires POD variable)
	@if [ -z "$(POD)" ]; then \
		echo "Error: POD not specified"; \
		echo "Usage: make describe-pod POD=hypercode-core-xxx"; \
		exit 1; \
	fi
	kubectl describe pod $(POD) -n $(NAMESPACE)

.PHONY: clean
clean: check-context ## Delete all resources (dangerous!)
	@echo "WARNING: This will delete all resources in namespace $(NAMESPACE)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		kubectl delete namespace $(NAMESPACE); \
	fi

.PHONY: clean-pvcs
clean-pvcs: ## Delete all PVCs (data will be lost!)
	@echo "WARNING: This will delete all data"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		kubectl delete pvc --all -n $(NAMESPACE); \
	fi
