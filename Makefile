.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

local-up: ## Bring up the full local stack (postgres + backend + frontend)
	cd local && docker compose up -d --build
	@echo ""
	@echo "Frontend:     http://localhost"
	@echo "Backend docs: http://localhost/api/docs"

local-down: ## Tear down the local stack and remove volumes
	cd local && docker compose down -v

local-logs: ## Tail logs from all local containers
	cd local && docker compose logs -f

cloud-plan: ## Show what Terraform would create
	cd infra/terraform && terraform init -upgrade && terraform plan

cloud-up: ## Deploy the full stack to AWS eu-central-1
	cd infra/terraform && terraform init -upgrade && terraform apply -auto-approve

cloud-down: ## Tear down all AWS resources
	cd infra/terraform && terraform destroy -auto-approve

cloud-outputs: ## Print Terraform outputs (URLs, endpoints)
	cd infra/terraform && terraform output

clean: local-down ## Clean local state and Terraform working files
	cd infra/terraform && rm -rf .terraform .terraform.lock.hcl
