# Tools Used

Per the CMPE433 project policy, this document lists AI tools used in producing
the codebase and the boundaries of their use.

## Claude (Anthropic) — for code and IaC generation only
Used for:
- Generating Terraform IaC templates (VPC, EC2, RDS, S3, Lambda, CloudWatch resources)
- Generating Dockerfiles, docker-compose configuration, nginx configuration
- Generating boilerplate application code: SQLAlchemy models, Pydantic schemas, FastAPI router scaffolding, the database seed script
- Debugging deployment errors

NOT used for:
- Writing any prose in this report or in docs/architecture.md, docs/shared-responsibility.md
- Producing architecture justifications or security analyses
- Generating the TCO numbers (these came from Phase 1, computed against the AWS Pricing Calculator by the team)

Every architectural decision in this project was made by the team. The team
can explain every line of code and every design choice without consulting
an LLM.
