V1.5.4 — Repo Boundaries And Activation Policy

## Goal

Lock the ownership boundaries between the main uDOS repo, internal extensions, companion
repos, and separate client app repos.

This decision exists to prevent architectural drift while v1.5.2 and v1.5.3 work continue.

## Canonical boundary

### Main uDOS repo owns
- core runtime
- `ucode`
- Wizard
- internal bundled extensions
- shared contracts consumed by companion servers and client apps

### Internal bundled extensions
Internal extensions live inside the main uDOS repo and are activated explicitly through
Wizard extension lifecycle controls.

Current internal extension policy:
- Empire remains internal to uDOS
- Empire is private and commercially developed
- Empire is not enabled by default
- Empire must be activated explicitly through Wizard Extensions, like the Dev extension lane

### Companion repo lane
Companion repos are not internal extensions even if they integrate tightly with uDOS.

Current companion repo policy:
- Sonic belongs in its own repository: `fredporter/uDOS-sonic`
- Sonic remains contract-compatible with Wizard and uDOS
- Sonic is consumed as an external local repo installed beside uDOS
- uDOS retains only the integration contract, Wizard GUI surfaces, loader hooks, and compatibility surface needed to interoperate with Sonic

### Separate server repos
- `uHOME-server` lives in its own main repository: `fredporter/uHOME-server`
- Wizard may surface `uHOME` status and controls, but the server implementation does not live in this repo

### Separate private client app repos
Commercial client apps remain outside the uDOS repo.

Current private app lanes:
- `uHOME-android-app`
- `OBSC-android-app`
- `OBSC-mac-app`

## Activation policy

### Wizard-gated internal extensions
Internal extensions must support:
- disabled-by-default operation
- explicit enable/disable lifecycle through Wizard
- stable status/health reporting when installed but disabled
- soft-fail behavior when not present or not enabled

Empire must follow this model.

### External companion products
External companion products do not share the same activation contract as internal extensions.

Sonic should instead follow:
- independent release/versioning
- explicit compatibility contracts with uDOS and Wizard
- pinned integration points
- no required submodule workflow

## Why this split

### Empire stays internal because
- it depends on core runtime and Wizard route contracts
- it owns provider-heavy business workflows tightly coupled to uDOS data and binder semantics
- it benefits from private extension activation rather than cross-repo distribution overhead

### Sonic moves out because
- it is install-first and independently runnable
- it has a standalone provisioning lifecycle
- it should version and release separately from the main runtime
- submodule-based coupling adds operational friction without enough architectural benefit

### uHOME server and apps stay separate because
- they are distinct deployment products
- they have their own release and commercial timelines
- they depend on uDOS contracts but should not be implemented inside this repo

## Contract impact

### uDOS docs must reflect
- Empire as an internal Wizard-activated extension
- Sonic as an external companion repo
- uHOME server and app repos as separate downstream consumers of uDOS contracts

### uDOS runtime should eventually reflect
- explicit Wizard Extension activation records for Empire
- compatibility manifests or pinned import references for Sonic
- no architectural language implying that client apps live in this repo

## Non-goals

- defining the Sonic sync mechanism in detail
- defining private app implementation details
- merging repo histories
- using git submodules as the preferred default

## Decision summary

- keep Empire internal and Wizard-activated
- move Sonic ownership to `uDOS-sonic`
- keep `uHOME-server` separate
- keep commercial macOS/Android apps in separate private repos
