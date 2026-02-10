# Library Service

Library status and integration management.

## Routes

- `GET /api/library/status`
  - Full library status snapshot.

- `GET /api/library/integration/{name}`
  - Integration details.

- `POST /api/library/integration/{name}/install`
- `POST /api/library/integration/{name}/enable`
- `POST /api/library/integration/{name}/disable`
- `DELETE /api/library/integration/{name}`

- `GET /api/library/enabled`
- `GET /api/library/available`
- `POST /api/library/refresh`
- `GET /api/library/stats`
- `GET /api/library/inventory`
