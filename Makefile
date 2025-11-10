# ============================================
# GenHack Climate - Makefile
# ============================================

.PHONY: help init build push deploy dryrun run clean test

# Configuration
PROJECT_ID ?= genhack-heat-dev
REGION ?= europe-west1
REGISTRY_LOCATION = europe
REGISTRY_NAME = heat
IMAGE_NAME = gh-pipeline
IMAGE_TAG ?= $(shell date +%Y%m%d-%H%M%S)
IMAGE_URL = $(REGISTRY_LOCATION)-docker.pkg.dev/$(PROJECT_ID)/$(REGISTRY_NAME)/$(IMAGE_NAME):$(IMAGE_TAG)
IMAGE_LATEST = $(REGISTRY_LOCATION)-docker.pkg.dev/$(PROJECT_ID)/$(REGISTRY_NAME)/$(IMAGE_NAME):latest
JOB_NAME = heat-downscaling-pipeline

help: ## Show this help message
	@echo "GenHack Climate Heat Downscaling - Make targets"
	@echo "================================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

init: ## Initialize GCP infrastructure (check Phase 0 setup)
	@echo "🔧 Checking infrastructure..."
	@bash infra/init-genhack.sh

build: ## Build Docker image locally
	@echo "🐳 Building Docker image..."
	@docker build \
		-f pipeline/Dockerfile.geo \
		-t $(IMAGE_URL) \
		-t $(IMAGE_LATEST) \
		--platform linux/amd64 \
		.
	@echo "✅ Built: $(IMAGE_URL)"

push: build ## Build and push Docker image to Artifact Registry
	@echo "📤 Pushing to Artifact Registry..."
	@gcloud auth configure-docker $(REGISTRY_LOCATION)-docker.pkg.dev --quiet
	@docker push $(IMAGE_URL)
	@docker push $(IMAGE_LATEST)
	@echo "✅ Pushed: $(IMAGE_URL)"

deploy: push ## Build, push, and deploy Cloud Run Job
	@echo "🚀 Deploying Cloud Run Job..."
	@IMAGE_TAG=$(IMAGE_TAG) bash infra/deploy_job.sh
	@echo "✅ Deployment complete!"

dryrun: ## Run pipeline locally with mock data
	@echo "🧪 Running pipeline locally (dry-run)..."
	@docker run --rm \
		-v $(PWD)/configs:/app/configs \
		-v /tmp/genhack:/tmp/genhack \
		-e PROJECT_ID=$(PROJECT_ID) \
		$(IMAGE_LATEST) \
		--config configs/paris_2022_mock.yml --dry-run
	@echo "✅ Dry-run complete! Check /tmp/genhack/exports/"

run: ## Execute Cloud Run Job
	@echo "▶️  Executing Cloud Run Job..."
	@gcloud run jobs execute $(JOB_NAME) \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--wait
	@echo "✅ Execution complete!"
	@echo ""
	@echo "View outputs:"
	@echo "  gsutil ls gs://gh-exports-$(PROJECT_ID)/paris/2022/"
	@echo ""
	@echo "View logs:"
	@echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$(JOB_NAME)\" --limit=50 --format=json"

logs: ## Tail Cloud Run Job logs
	@echo "📋 Fetching logs..."
	@gcloud logging read \
		"resource.type=cloud_run_job AND resource.labels.job_name=$(JOB_NAME)" \
		--limit=50 \
		--format=json \
		--project=$(PROJECT_ID)

clean: ## Clean local artifacts
	@echo "🧹 Cleaning local artifacts..."
	@rm -rf /tmp/genhack/*
	@docker image prune -f
	@echo "✅ Cleaned!"

test: ## Run contract tests
	@echo "🧪 Running tests..."
	@python -m pytest tests/ -v
	@echo "✅ Tests passed!"

verify: ## Verify no Kura references in code
	@echo "🔍 Scanning for Kura references..."
	@if grep -r "mental-journal-dev" src/ pipeline/ configs/ 2>/dev/null; then \
		echo "❌ Found Kura references!"; \
		exit 1; \
	else \
		echo "✅ No Kura references found"; \
	fi

status: ## Check deployment status
	@echo "📊 Deployment Status"
	@echo "==================="
	@echo ""
	@echo "Cloud Run Job:"
	@gcloud run jobs describe $(JOB_NAME) \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--format="table(name,lastExecutionStatus,lastExecutionTime)" 2>/dev/null || echo "  Not deployed"
	@echo ""
	@echo "Latest executions:"
	@gcloud run jobs executions list \
		--job=$(JOB_NAME) \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--limit=5 \
		--format="table(name,status,startTime)" 2>/dev/null || echo "  No executions"

.DEFAULT_GOAL := help
