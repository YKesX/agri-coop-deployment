# Contributors

This monorepo consolidates work from three team-member repositories, plus
integration, refinement, and unification work by the integration lead.

## Source repositories (imported)

- `apps/backend/` originated from https://github.com/clammus/farmer_app_backend
  (extended significantly: SQLAlchemy ORM, Pydantic schemas, routers, real DB queries)
- `apps/frontend/` originated from https://github.com/Caganakirmak/cooperative-web-frontend
  (rewritten as a mobile-responsive single-page dashboard with API integration)
- `apps/backend/seed/farmers_data.csv` originated from https://github.com/ege-dnc/CMPE433-VPC

## Integration and refinement

- Yagizhan Kesgin (@YKesX) — monorepo consolidation, unified Terraform across all
  services, application refinement, local development stack, libvirt networks for
  the virtualization demo, documentation skeleton, Makefile, one-click deployment
