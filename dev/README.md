# Dev Mode Extension Framework

The `/dev` directory is the Dev Mode extension framework for uDOS v1.5.

It exists to provide:
- Dev Mode governance files
- contributor workflow templates
- roadmap, task, and summary storage
- extension metadata used to gate Dev Mode activation
- contributor test policy and release-readiness workflows

Rules:

- standard runtime remains `ucode`
- Dev Mode is entered implicitly only after the `dev` profile and `dev-mode` extension are active
- Wizard GUI owns install, uninstall, activation, and deactivation
- `/dev` is the versioned distro/template scaffold
- local mutable contributor data must stay separate from the template truth
- executable pytest entrypoints remain in root `scripts/`

It must not contain production runtime code. Wizard owns the live Dev Mode runtime and TUI/Dev tooling integration.
