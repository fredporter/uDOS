# Wizard Server Roadmap

**Component:** `wizard/` | **Current:** v1.3.12 | **Status:** Active Development

---

## Completed (v1.3.x)

- [x] Consolidated wizard code (api/wizard + mcp/wizard merged into wizard/)
- [x] MCP gateway and server scaffolding (`mcp/gateway.py`, `mcp/server.py`)
- [x] Plugin registry and stub routes
- [x] Container launcher and proxy routes
- [x] Library routes foundation
- [x] Beacon implementation
- [x] Port manager / CLI port manager
- [x] Audio transport service refactor (split)

---

## v1.4.0

### P0 -- Must Have

- [ ] Library manager completion -- full CRUD, versioning, dependency resolution
- [ ] Web proxy implementation -- reverse proxy for container-hosted services
- [ ] Workspace routing -- `@workspace` syntax for routing requests to named contexts
- [ ] MCP gateway hardening -- auth, rate limiting, tool registration protocol
- [ ] Unified config layer -- single config source of truth across wizard/

### P1 -- Should Have

- [ ] Container orchestration -- compose-based multi-container lifecycle management
- [ ] Plugin marketplace -- discovery, install, update flow via plugin registry
- [ ] Provider health checks -- automated provider availability monitoring
- [ ] Extension hot-reload -- live reload for wizard extensions without restart
- [ ] Dashboard WebSocket events -- real-time status push to web-admin

### P2 -- Nice to Have

- [ ] Self-heal route expansion -- broader automated recovery strategies
- [ ] Diagram generation service -- server-side diagram rendering pipeline
- [ ] Songscribe route integration -- bridge groovebox transport into wizard API
- [ ] GitHub integration polish -- PR/issue automation helpers

---

## v1.5.0 (Planned)

- [ ] Multi-tenant workspace isolation
- [ ] Distributed wizard nodes (cluster mode)
- [ ] Audit log and compliance layer

---

## Dependencies

| Item | Depends On |
|---|---|
| Web proxy | Container orchestration basics |
| Plugin marketplace | Library manager completion |
| Workspace routing | Unified config layer |
| MCP gateway hardening | MCP server stabilization |
| Songscribe routes | groovebox/transport audio pipeline |
| Dashboard WebSocket | Web-admin frontend (web-admin/) |
