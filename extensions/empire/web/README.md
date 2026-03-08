# Empire Web Status

This standalone web app is a legacy reference surface.

Current contract:

- Empire is an internal uDOS extension.
- The supported runtime UI is the Wizard dashboard route at `#empire`.
- This `extensions/empire/web` app is not the canonical runtime surface.
- This app is not part of the active v1.5.2 release gate.
- Keep it only for legacy reference, local experimentation, or controlled migration support.

If product-critical UI work is needed, implement it in the Wizard-owned Empire route instead of expanding this standalone web surface.
