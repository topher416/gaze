# The Gaze — Progress Document
## Last updated: 2026-05-05
## Session: Bottleneck analysis → Texture pipeline → Asset embed → Deploy

## ── Current State ──
The game is live at topherrasmussen.com/gaze.html with:
- Raycaster engine with **ComfyUI-generated tileable textures** (stone, mirror, door)
- All Canvas2D procedural generators removed (replaced by embedded textures)
- Touch controls (left joystick move, right drag look) — **fixed: added e.preventDefault() to title/death screen touchstart to prevent mobile scroll interference**
- Enemy chase AI (simple approach player)
- Desire/drain pickup system
- Death screen + respawn
- Tone.js ambient audio
- **v0.3 deployed** — ComfyUI sprite textures (enemy reflection + pickup desire), 10.2MB total
  - Enemy reflection: 256×320, 157KB, emaciated humanoid with red eye
  - Pickup desire: 128×128, 30KB, glowing orb
  - Pain/dead states: Canvas2D overlays preserved (red overlay, dissolving eye)
- **v0.2.2** — 9.5MB, 3 embedded tileable textures (stone, mirror, door) + mobile tap fix
- All textures tested locally, zero JS errors, mobile tap working

## ── What Changed This Session ──

### Infrastructure Built
- ✅ `~/gaze/generate_textures.py` — batch texture queue via ComfyUI REST API
- ✅ `~/gaze/embed_textures.py` — converts PNGs to base64, injects into HTML
- ✅ `~/gaze/text_overlay.py` — Lacanian text PIL overlay (scrapped — didn't like it)
- ✅ `~/gaze/deploy.sh` — dual-repo sync script with auth guardrails
- ✅ `~/gaze/GAZE_MECHANIC.md` — interaction design doc (mutual gaze mechanic)
- ✅ `~/gaze/PLAN.md` — step-by-step action plan
- ✅ `~/gaze/ASSET_INVENTORY.md` — texture/sprite tracking

### Textures Generated (tileable, 1024×1024, SD 1.5)
| Asset | Status | Size | Notes |
|-------|--------|------|-------|
| stone_wall_tileable | ✅ embedded | 2.3MB | Strong — good depth, seamless |
| mirror_wall_tileable | ✅ embedded | 2.6MB | More damask/baroque than mirror |
| door_wall_tileable | ✅ embedded | 2.3MB | Ornamental pattern, not door-adjacency |
| stone_wall_alt_tileable | ⏭ skipped | 2.6MB | Reads as contour map, not usable |
| floor_stone_tileable | ⏭ not needed | 2.3MB | Game uses flat colors for floor/ceiling |

### Corrupted Files Cleaned
- ✅ Deleted 26-byte corrupted `flux-schnell-fp8.safetensors`

### Files Modified
- `~/gaze/index.html` — 31KB → 19.8MB (3 texture embeddings + Canvas2D guards)
- Pushed to both repos (topher416/gaze + topher416/topherrasmussen.github.io)

## ── Bottlenecks Identified ──
1. **Model download instability** — Flux downloads fail repeatedly
2. **SD 1.5 prompt limitations** — mirror/door textures didn't come out right
3. **Single-file HTML bloat** — 19MB is large but functional
4. **Deployment friction** — manual dual-repo push (deploy.sh automates but not tested yet)
5. **Undefined gaze mechanic** — core interaction still TBD (design doc written, not implemented)

## ── What We Abandoned ──
- **Baked-in Lacanian text overlays** — text hard to see, user doesn't read French
- **stone_alt_tileable** — looks like topographic map, not stone
- **Canvas2D procedural art** — superseded by ComfyUI textures

## ── File Locations ──
- Game repo: `~/gaze/` → `topher416/gaze`
- Live site: `topherrasmussen.com/gaze.html` ← `topher416/topherrasmussen.github.io`
- Textures: `/tmp/gaze_textures/` (source PNGs)
- ComfyUI: `~/Documents/comfy/ComfyUI/` (localhost:8188, lowvram mode)
- ComfyUI output: `~/Documents/comfy/ComfyUI/output/`
- Generated previews: `/tmp/gaze_preview/`

## ── ComfyUI Setup ──
- Server: `http://127.0.0.1:8188`, lowvram mode
- Models: `v1-5-pruned-emaonly.safetensors` (4GB SD 1.5)
- Python 3.11.15 in .venv
- Corrupted flux model deleted, not replaced yet

## ── Next Steps ──
1. Verify live site CDN update (check in 10-15 min)
2. Mirror texture quality — consider regenerating with different prompts
3. Define gaze mechanic implementation (see GAZE_MECHANIC.md)
4. Generate sprite textures (enemies, pickups)
5. Deploy gaze mechanic changes
