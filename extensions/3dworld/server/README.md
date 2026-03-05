# 3dworld Server Lane

This folder is the dedicated runtime lane placeholder for 3DWORLD.

Expected responsibilities:
- start/stop 3D render sessions
- map core gameplay snapshot -> 3D scene state
- stream interaction events back to canonical gameplay runtime

Do not persist canonical gameplay state in this extension lane.
