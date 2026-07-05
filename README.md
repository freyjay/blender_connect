# blender_connect

Senses and tooling for an AI agent (Claude) driving Blender over MCP.

## What this is
Claude connects to Blender through the official Blender MCP (addon + server).
Code execution and scene queries work perfectly; image transport proved
unreliable (downscaled to fit a ~786KB budget, illegible on arrival).
This project gives the agent working senses anyway: **math as the primary
eye**, rendered as text, which always survives transport.

## Components
- `eye.py` -- ASCII vision system. Orthographic ray-cast renderer
  (per-object letter mode + depth-gradient mode) and 1-D `scanline()` probes.
  Runs inside Blender's Python.
- `PATCHES.md` -- local fix applied to the Blender MCP addon
  (upstream issue #21, truncated socket sends) and screenshot-toolcode findings.
- `tasks/blueprint.md` -- project vision. `tasks/todo.md` -- roadmap.

## Usage (inside Blender / via MCP execute)
```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/Developer/blender_connect"))
from eye import render_ascii, scanline
print(render_ascii(view="FRONT", width=64, height=32, mode="id"))
```

## Development flow
Experiments happen in `~/Developer/blender-connect-experiment` (local only).
Proven code gets promoted here and pushed to GitHub.
