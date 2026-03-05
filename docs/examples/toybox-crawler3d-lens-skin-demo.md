# TOYBOX Crawler3D Lens + Skin Demo

## Goal

Run crawler3d with the shared lens/skin contract and scaffold GUI skin insertion via `ucode`.

## Flow

```bash
PLAY TOYBOX SET crawler3d
PLAY LENS SET crawler3d
PLAY LENS STATUS

SKIN SCAFFOLD nes
SKIN INSERT nes CSS .crawler-hud { border: 1px solid #7df; }
SKIN INSERT nes SLOT hud <div class=\"crawler-hud\">Crawler3D HUD Active</div>
SKIN CHECK

# 3D extension lane (separate advanced GUI runtime)
# extension metadata: extensions/3dworld/extension.json
```

## Expected

- `PLAY LENS` reports crawler3d lens state
- skin scaffold files are created under `themes/nes/assets/`
- CSS and slot payload insertion records are persisted
- 3D extension lane remains separate from core gameplay persistence
