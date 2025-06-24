# 🗺️ uDOS Roadmap: Sandbox and Share Scripts
**Archived on:** 2025-06-24

This document outlines deprecated scripts and plans for uScript modular evolution.

| Script | Purpose | Status | Planned Migration |
|--------|---------|--------|--------------------|
| `sandbox_draft.sh` | Create a working draft in the sandbox folder | Deprecated | Include in uScript v0.2 sandbox lifecycle pipeline with identity-aware tracking |
| `sandbox_finalise.sh` | Finalise and move sandbox draft to logged state | Deprecated | Merge with log_x.sh templates once full identity state tracking is available |
| `accept_share.sh` | Accept, decrypt, and validate incoming shared file | Deprecated | Move into a uScript called `share-accept` with PKI signature checks |
| `authorise_share.sh` | Generate outbound share request and approval | Deprecated | Move into uScript called `share-authorise` with NFT-bound consent chain |