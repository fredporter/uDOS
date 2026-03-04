# Wizard Web App Status

The embedded Wizard web app has moved to an independent project.

This repository no longer ships or runs `wizard.web.app`.

## Startup in this repo

Use the local startup script to run the canonical Wizard server runtime:

```bash
./wizard/web/start_wizard_web.sh
```

That script delegates to the canonical daemon launcher:

```bash
./bin/udos wizard start
```
