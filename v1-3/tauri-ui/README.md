# tauri-ui (optional desktop control plane)

Use Tauri for “app UI” needs:
- missions dashboard
- job queue view
- approvals / contribution review
- permissions management

Publishing/browsing should remain static HTML (theme packs), served locally or opened as files.

Tauri can:
- call local binaries (core CLI)
- use local IPC
- optionally host an embedded HTTP server when needed (but not required for simple browsing)
