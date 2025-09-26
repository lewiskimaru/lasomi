# Lasomi — Product & System Design Blueprint

> Single-source platform for telecom project lifecycle: Survey → Design → Construction → Documentation → Handover

This document is a practical, modular blueprint you can use to build Lasomi from MVP → production. It contains product principles, modular scope (stage-by-stage), an MVP definition, UX/workflows, canonical data model, system architecture, tech stack recommendations, exports & integrations, operational concerns, KPIs, a staged roadmap, team/roles, a go-to-internal adoption plan, risks & mitigations, and next actions.

---

# 1. Product principles (guiding north stars)
- **One place to live:** engineers start and finish work inside Lasomi (export only for external stakeholders).  
- **Human-in-the-loop automation:** automation does heavy lifting; people review & accept.  
- **Modular & pluggable:** build modules (Survey, Drive, Designer, Construction, Handover) independently.  
- **Provenance & traceability:** every asset has source, confidence, created_by, created_at.  
- **Design-first:** polished, predictable UI and minimal cognitive load.

---

# 2. High-level product modules (minimal to full)
1. **Survey App (Mobile + Web capture)**
   - Mobile PWA for field capture (offline), built-in telecom layers (poles, manholes, buildings), structured forms (photos, notes, attributes), GNSS/RTK input.  
   - Auto-sync to Data Drive; generate survey report (PDF/Word) automatically.  
2. **Data Drive (central storage + assets)**
   - PostGIS-backed repository with attachments (S3).  
   - File viewer, image editor (crop/annotate/arrow), search, versioning, exports (GeoJSON/KMZ/GPkg).  
3. **Designer (Endless Canvas + Map Overlay)**
   - Map overlay (vector tiles) + infinite canvas with drawing tools (centerlines, splice points, OLT).  
   - Automations: building extraction, accessorize rules, clustering engine, route suggestions.  
   - Rule profiles per project type (FTTH, FTTB, FTTS).  
4. **Construction Packs & Handover**
   - Produce crew bundles: KMZ, accessory CSV, BOM Excel, PDF map sheets, OTDR placeholders.  
   - Field sync back to Lasomi (as-built ingestion).  
5. **Collaboration & Project Management**
   - Tasks, assignments, timelines, comments, approvals, audit log.  
   - Integrations: Slack/Teams, ClickUp/Jira (optional), Email & Webhooks.

---

# 3. MVP scope (what to build first)
**Goal:** replace repetitive junior tasks and prove time-savings.

**MVP modules:**
- Survey App (PWA) with offline capture + upload to Drive.  
- Data Drive with PostGIS, attachments, basic search, and image annotate tool.  
- Designer (read-only): import KMZ, draw AOI, auto-extract buildings (MS + Google + OSM), export KMZ/GeoJSON.  
- Simple accessory rule engine + accessories CSV export.  
- Basic collaboration: Projects, users, tasks, comments.  

**MVP success metric:** reduce average manual tracing time per AOI by 60% for pilot users.

---

# 4. UX / Key workflows (concise)
1. **Field survey**: login → pick project → preloaded basemap & layers → capture feature (point/polygon/photo/form) → offline sync → Story/Report auto-generated in Drive.  
2. **Designer review**: open AOI → run auto-extract → confidence heatmap → bulk-accept → run accessorize
engine → preview accessories per pole → export construction bundle.  
3. **Construction**: PM generates crew bundle → crew sync with mobile app → update as-built → closed loop.

---

# 5. Canonical data model (PostGIS simplified)
- **projects(id, name, owner, meta)**  
- **aois(id, project_id, polygon, status, source_kmz)**  
- **buildings(id, aoi_id, geom(polygon), centroid, source, source_id, confidence, type, tenants)**  
- **roads(id, aoi_id, geom(linestring), name, source)**  
- **poles(id, aoi_id, geom(point), height_m, pole_type, equipment_json)**  
- **accessories(id, pole_id, code, desc, qty, rule_id, reason)**  
- **clusters(id, aoi_id, dp_location, member_buildings, total_tenants, recommended_split)**  
- **attachments(id, entity_type, entity_id, url, type, metadata)**  
- **rule_profiles(id, name, rules_json, project_id)**  
- **exports(id, aoi_id, type, file_url, meta)**  
- **audit_logs(user,action,entity,details,timestamp)**

Indexes: GIST on all geom columns, btree on confidence, created_at.

---

# 6. System architecture (recommended stack)
**Frontend:** React + MapLibre GL (Mapbox-compatible but OSS) + Tailwind/Tailwind UI (fast design)  
**Mobile:** PWA (React) or Capacitor wrapper for native features (camera, GPS); offline storage via IndexedDB  
**API:** FastAPI (what you use) → expand with OpenAPI + auth middleware  
**DB:** Postgres + PostGIS (managed: Supabase / AWS RDS)  
**Processing:** Celery / RQ + Redis for ETL (AOI clip, tile build, accessorize jobs)  
**Tiles:** Tippecanoe → MBTiles served by tileserver-gl or self-hosted vector-tile server; S3 for storage  
**Storage:** S3-compatible (images, exports)  
**Auth:** SSO (Google Workspace / Okta) + role-based ACL  
**Hosting:** initial: Render / Fly / Railway / Vercel for frontend, Cloud Run or ECS for backend; scale to Kubernetes later  
**CI/CD:** GitHub Actions → build, test, deploy  

---

# 7. Rule engine & automations (design pattern)
- Store rules as JSON/YAML in `rule_profiles`.  
- Worker evaluates rules per entity (predicate → action) and appends `explain` text.  
- Rules examples: span thresholds, splice_at_pole, drop_accessory, clustering params.  
- Provide rule editor UI for power users (copy/profile/versions).  

---

# 8. Integrations & export formats
- **Exports:** KMZ (visual + photos), GeoJSON, GeoPackage, CSV/Excel (BOM), PDF map sheets, DWG (optional via CAD contractor).  
- **Field sync:** generate Field Maps or Fulcrum-ready GeoPackage bundles.  
- **External tools:** Webhooks/REST to ClickUp/Jira, SFTP for large bundles.  
- **POI & maps:** primary = OSM + Geofabrik, optionally enrich on demand using Google Places/Mapbox (watch license & costs).  

---

# 9. Security, provenance & licensing
- Always store `source`, `source_id`, `license`, `retrieved_at` on imported features.  
- Include `LICENSES.txt` in every export bundle.  
- Access control by project + role.  
- Audit logs for acceptance/exports.  

---

# 10. Metrics & OKRs (track these)
- **Time to produce AOI** (pre vs post automation) — target: -60% in pilot  
- **% of features accepted without edit** — target: >70% after tuning  
- **Exports/day** and **AOIs processed/week**  
- **Field rework tickets** (downstream) — target: -30% after 3 months  
- **Active users (junior / senior)**

---

# 11. 6–12 month staged roadmap (release plan)
**Phase 0 — Discovery (1–2 weeks)**: interviews, collect sample AOIs, baseline metrics.  
**Phase 1 — MVP (6–10 weeks)**: Survey PWA + Data Drive + Auto-extract + accessory CSV export + basic tasks.  
**Phase 2 — Designer + Rule Engine (8–12 weeks)**: Endless canvas, rule editor, cluster engine, MBTiles, exports.  
**Phase 3 — Field sync & As-built (6–8 weeks)**: Field Maps integration, as-built ingestion, approvals.  
**Phase 4 — Scale & polish (ongoing)**: performance, RBAC, admin UI, plugins (FTTx templates, vendor parts).  

---

# 12. Team & roles (lean org for POC)
- **You (Product/Domain Lead)** — define rules, gather requirements, pilot with teams.  
- **1 Backend Engineer** (FastAPI, PostGIS, Celery)  
- **1 Frontend Engineer** (React + MapLibre)  
- **1 Mobile/Fullstack** (PWA offline) or use web PWA only  
- **1 DevOps/Infra (part-time)**  
- **1 UX/Product Designer (part-time)** — to make it look polished  
- **1 Senior Engineer (domain champion)** — stakeholder and reviewer (could be an internal senior designer)  

Keep the team small for first 3 releases; recruit contractors for UI or tile work if needed.

---

# 13. Adoption & internal rollout plan
1. **Pilot** with 1 senior + 3 juniors for 4 weeks — collect before/after metrics.  
2. **Training kit**: 2 short videos, 1-page cheat sheet per role, and an onboarding session.  
3. **Showcase**: 1 internal lunch demo + case study (time saved) — convert into exec ask for resources.  
4. **Governance**: rule profile owners, export approval process, schedule monthly reviews.

---

# 14. Monetization / long-term options
- License to small ISPs / contractors as SaaS (per-AOI or per-seat pricing)  
- Managed data/analysis services (AOI extraction for customers)  
- Premium features: advanced clustering,optimize BOM, vendor parts pricelists, OSS/BSS integrations.

---

# 15. Risks & mitigations (practical)
- **License issues (Maps/POIs)**: Mitigate by favoring OSM + clear LICENSES metadata and on-demand paid enrichment.  
- **Data trust**: show confidence scores, human-in-loop edits, provenance.  
- **Scale/perf**: vector tiles, MBTiles, background workers.  
- **Adoption**: small pilot, senior champion, focused training.

---

# 16. Next 7-day checklist (practical)
1. Run 3 stakeholder interviews (1 senior, 2 juniors, 1 PM).  
2. Collect 5 representative AOIs (small/medium/large).  
3. Build a minimal PostGIS schema and ingest one AOI.  
4. Implement one accessory rule and export CSV (end-to-end).  
5. Prepare 1-page pilot case study template (before/after metrics).

---

# 17. Deliverables I can produce for you right now
- SQL DDL for PostGIS tables (ready to paste).  
- JSON rule profile template with span/drop/splice rules.  
- OpenAPI skeleton for FastAPI endpoints (upload KMZ, run extract, export).  
- 1-page UX spec (screens + CTAs) for Junior/ Senior flows.

Tell me which of the four (SQL / Rule JSON / OpenAPI skeleton / UX spec) you want me to generate in this conversation and I will add it into the project docs.

