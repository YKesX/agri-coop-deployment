# Contributors

This monorepo consolidates work from three team-member repositories, plus
integration, refinement, and unification work by the integration lead.

## Source repositories (imported)

- Selçuk Solmaz (@clammus) 
  `apps/backend/` originated from https://github.com/clammus/farmer_app_backend
  (extended significantly: SQLAlchemy ORM, Pydantic schemas, routers, real DB queries)
- Çağan Akırmak (@Caganakirmak)
  `apps/frontend/` originated from https://github.com/Caganakirmak/cooperative-web-frontend
  (rewritten as a mobile-responsive single-page dashboard with API integration)
- Ege Dinçer (@ege-dnc)
  `apps/backend/seed/farmers_data.csv` originated from https://github.com/ege-dnc/CMPE433-VPC

## Integration and refinement

- Yağızhan Keskin (@YKesX) — monorepo consolidation, unified Terraform across all
  services, application refinement, local development stack, libvirt networks for
  the virtualization demo, documentation skeleton, Makefile, one-click deployment
