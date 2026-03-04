# Privacy

Effective date: 2026-03-04

uDOS is an offline-first open-source system. The default runtime keeps user data local, with optional provider integrations configured explicitly by the operator.

## Public Policy

- No built-in telemetry is required for local operation.
- API credentials stay in local environment files controlled by the operator.
- Wizard networked features are optional and operator-configured.
- Logs are local runtime artifacts, not remote collection surfaces.

## Operator Notes

- Review `.env` and provider settings before enabling Wizard integrations.
- Keep secrets local and out of git.
- Back up important local runtime data before destructive operations.

## References

- Installation and setup: [INSTALLATION.md](/Users/fredbook/Code/uDOS/docs/INSTALLATION.md)
- Public docs front door: [README.md](/Users/fredbook/Code/uDOS/docs/README.md)
- Credits and attribution: [credits.md](/Users/fredbook/Code/uDOS/wiki/credits.md)
- License: [LICENSE](/Users/fredbook/Code/uDOS/LICENSE)
