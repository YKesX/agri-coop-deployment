# Sanliurfa Agricultural Cooperative — Cloud Migration

A unified cloud and local development stack for a fictional agricultural cooperative in Sanliurfa, Turkey. The system provides a FastAPI backend connected to PostgreSQL, a responsive web dashboard, a scheduled Lambda for soil moisture monitoring, and full AWS infrastructure defined as Terraform IaC. Built as a CMPE433 (Atilim University) Phase 2 project.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Terraform >= 1.6
- AWS CLI configured with credentials (for cloud deployment)
- An email address for CloudWatch alarm subscriptions

## Run locally in 30 seconds

```bash
make local-up
```

Open http://localhost for the dashboard, http://localhost/api/docs for the API.

## Deploy to AWS in 5 minutes

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set your email and GitHub repo URL
```

```bash
make cloud-up
```

After deployment completes (~5 minutes):
1. Confirm the SNS subscription email from AWS
2. Open the URL from `make cloud-outputs` to see the live dashboard

## Tear down

```bash
# Local
make local-down

# AWS (removes everything including S3 bucket)
make cloud-down
```

## Repository layout

```
agri-coop-deployment/
├── README.md
├── Makefile
├── CONTRIBUTORS.md
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── shared-responsibility.md
│   └── tools-used.md
├── apps/
│   ├── backend/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── farmers.py
│   │   │   ├── villages.py
│   │   │   ├── crops.py
│   │   │   ├── sensors.py
│   │   │   ├── alerts.py
│   │   │   └── stats.py
│   │   ├── seed/
│   │   │   ├── schema.sql
│   │   │   ├── seed.py
│   │   │   └── farmers_data.csv
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── Procfile
│   │   └── sensor_data.json
│   ├── frontend/
│   │   ├── index.html
│   │   ├── style.css
│   │   ├── app.js
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   └── lambda-sensor-processor/
│       ├── handler.py
│       ├── requirements.txt
│       └── README.md
├── infra/
│   └── terraform/
│       ├── versions.tf
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── network.tf
│       ├── security.tf
│       ├── iam.tf
│       ├── compute.tf
│       ├── database.tf
│       ├── storage.tf
│       ├── lambda.tf
│       ├── monitoring.tf
│       ├── user_data.sh
│       └── terraform.tfvars.example
└── local/
    ├── docker-compose.yml
    ├── docker-compose.cloud.yml
    ├── .env.example
    ├── README.md
    └── libvirt/
        ├── agri-public-net.xml
        ├── agri-private-net.xml
        └── README.md
```

<!-- TODO: screenshot of dashboard -->

For architecture rationale and design decisions, see [docs/architecture.md](docs/architecture.md).
