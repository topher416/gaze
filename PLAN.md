# The Gaze — Step-by-Step Action Plan

## Phase 0 — Clean Up (15 min)
### Step 1: Audit and clean corrupted files
```bash
# Delete the corrupted 26-byte Flux file
rm ~/Documents/comfy/ComfyUI/models/checkpoints/flux-schnell-fp8.safetensors

# Verify what's left — only working models should remain
ls -lh ~/Documents/comfy/ComfyUI/models/checkpoints/
# Expected: v1-5-pruned-emaonly.safetensors (4GB) only

# Verify gaze repo state — check index.html actually matches live site
curl -s "https://topherrasmussen.com/gaze.html" | head -5
curl -s "https://raw.githubusercontent.com/topher416/gaze/main/index.html" | head -5
# If they differ, we'll sync them in Phase 4
```
**Acceptance:** No corrupted files on disk, clear picture of code sync state.

---

## Phase 1 — Unblock the Art Pipeline (2-3 hours, can run in background)
### Step 2: Get a working high-capability model running
**Decision point** — try Flux again or use proven SD 1.5 with smarter prompts?

**Option A: Retry Flux (text rendering capability)**
```bash
# Download from the correct official source
cd ~/Documents/comfy/ComfyUI/models/diffusion_models
curl -L -o flux1-schnell-fp8.safetensors \
  "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell-fp8.safetensors"
# Also need text encoders in models/text_encoders/
# This will take ~8-10 min at 30MB/s
```

**Option B: Stick with SD 1.5 + Canvas2D text overlay (PROVEN, ships faster)**
- Use what works: SD 1.5 for base textures (already 30s/image on M4)
- Canvas2D handles text rendering (Latin quotes rendered via font, not AI)
- Hybrid approach: AI generates texture, Canvas2D draws Lacanian text on top
- No download needed — just better prompt engineering

**Recommendation: Option B for now.** Flux adds model size (5-16GB), longer generation times, and SDXL needs more RAM than the M4's 16GB comfortably provides in lowvram mode. Text rendering is solved by Canvas2D — don't pay AI complexity for a problem with a simple solution.

### Step 3: Improve texture generation prompts
Current prompts generate "scenes" instead of "tileable textures." Fix the prompts:

```
Positive prompt:
"scratchboard etching texture, seamless repeating pattern, 
gothic stone wall, monochromatic with rust-red and gold highlights, 
dramatic chiaroscuro, no focal point, no human figures, 
uniform surface suitable for 3D wall tiling, ps5 era game texture,
--v 5 --tile"

Negative prompt:
"people, faces, text, focal point, perspective, scene composition,
entryway, doorway, horizon, sky, ground plane"
```

Key additions: `--tile` (SD parameter), "seamless repeating pattern", "no focal point", "uniform surface"

### Step 4: Set up batch texture queue via ComfyUI API
Instead of one-at-a-time through the UI:

```bash
# Create a Python script that queues all textures via REST API
# ~/gaze/generate_textures.py
# - Reads texture list (wall types, sprite types)
# - Sends to localhost:8188/prompt for each
# - Monitors progress, saves results to /tmp/gaze_textures/
```

**Textures to generate (priority order):**
1. `stone_wall` — 1024×1024, tileable
2. `mirror_wall` — cracked mirror frame pattern
3. `door` — ornate gothic door pattern (doorways, not full doors in context)
4. `stone_alt` — variation for visual diversity
5. `mirror_alt` — variation
6. `floor` — if floor tiles are used

**Sprite textures (after walls):**
- `enemy_reflection` — 80×96, humanoid silhouette, 4 states (idle/chase/pain/dead)
- `enemy_gaze` — 128×96, eye motif, 4 states
- `enemy_mirror` — 80×80, cracked frame, 4 states
- `pickup_desire` — orb/glow collectible
- `weapon` — first-person weapon sprite (if kept)

**Acceptance:** All 6 base textures generated as 1024×1024 PNGs in /tmp/gaze_textures/, verified tileable quality.

---

## Phase 2 — Define the Gaze Mechanic (30 min thinking, write 1 page)
### Step 5: Interaction design document
Write a 1-page `~/gaze/GAZE_MECHANIC.md` that specifies:

1. **What "looking at" means:** Which screen area? Center? Player-facing direction? Eye tracking (no, too complex)? Duration-based attention?

2. **What happens when observed:** Does the reflection transform? Does it move toward you? Does it speak (text, audio)? Does Desire drain faster?

3. **How does the player interact back:** Do they "look away" to calm it? Is there a gaze duration threshold? Do multiple reflections compound?

4. **Victory/loss conditions:** What ends the game? What does "winning" mean in a non-shooter?

5. **State machine additions:** What new states do enemies get? (Noticed → Watching → Approaching → ???)

**Acceptance:** Written document that an engineer could implement from without guessing.

---

## Phase 3 — Build the Pipeline (1-2 hours)
### Step 6: Create sprite/texture inventory
Write `~/gaze/ASSET_INVENTORY.md`:

| Asset | Type | Size | Status | Source | Priority |
|-------|------|------|--------|--------|----------|
| stone_wall | wall texture | 1024×1024 | ✅ 567K | SD 1.5 (regenerate with --tile) | P0 |
| mirror_wall | wall texture | 1024×1024 | ✅ 2.1MB | SD 1.5 (regenerate with --tile) | P0 |
| door | wall texture | 1024×1024 | ✅ 2.1MB | SD 1.5 (regenerate with --tile) | P0 |
| enemy_reflection | sprite | 80×96×4 states | ❌ | SD 1.5/Flux | P1 |
| enemy_gaze | sprite | 128×96×4 states | ❌ | SD 1.5/Flux | P1 |
| pickup_desire | sprite | 32×32 | ❌ | Canvas2D is fine | P2 |

Plus: who's generating, eta, quality criteria.

### Step 7: Build hybrid text overlay system
For Lacanian quotes on walls:

```javascript
// Overlay approach (runs during texture embed step):
// 1. Load AI-generated texture as image
// 2. Create offscreen canvas at 1024×1024
// 3. Draw texture to canvas
// 4. Set font: serif, italic, 48px
// 5. Draw text: "Je pense là où je ne suis pas"
//    - Use low opacity (0.3-0.5) so text feels etched into stone, not pasted on
//    - Add slight texture blur to text edges for integration
//    - Position: center, rotated slightly, or scattered across surface
// 6. Export as PNG, base64 encode for embed

// Quotes to include:
// "Je pense là où je ne suis pas"
// "L'Autre"
// "Désir de l'Autre"
// "Il n'y a pas de rapport sexuel"
// "Le signifié flotte sous le signifiant"
// "Le réel, c'est l'impossible"
```

**Acceptance:** 3-4 wall texture variants with Lacanian text rendered via Canvas2D, visually integrated (not pasted-on look).

---

## Phase 4 — Integration and Deploy (30 min)
### Step 8: Build deployment automation
Create `~/gaze/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "=== Building Gaze ==="
# Step 1: Inline all textures into index.html
python3 embed_textures.py  # reads PNGs from /tmp/gaze_textures/, updates index.html

echo "=== Pushing to gaze repo ==="
cd ~/gaze
git add index.html
git commit -m "v0.2.1: updated textures"
git push origin main

echo "=== Syncing to personal site ==="
cp index.html /tmp/personal-site/gaze.html
cd /tmp/personal-site
git add gaze.html
git commit -m "sync gaze v0.2.1"
git push origin main

echo "=== Verifying deployment ==="
echo "Checking raw GitHub..."
curl -s "https://raw.githubusercontent.com/topher416/gaze/main/index.html" | grep -o "v0.2.1" || echo "⚠ Not on raw GitHub yet"

echo "Check live site at: https://topherrasmussen.com/gaze.html"
echo "CDN may lag 5-15 minutes. Force refresh: Cmd+Shift+R"
```

**Acceptance:** One command deploys to both repos, verifies raw GitHub has the new version, prints live URL.

### Step 9: Generate, embed, deploy
The actual production run:

1. Run ComfyUI batch texture generation (Step 4)
2. Run Canvas2D text overlay generation (Step 7)
3. Run embed script to update index.html
4. Run deploy.sh
5. Verify at raw GitHub URL immediately
6. Check live site after 5 minutes

**Acceptance:** Live site shows PS5-quality etched textures with Lacanian text visible on walls.

---

## Execution Order and Dependencies

```
Phase 0 (15 min) ──────────────────────┐
                                      ↓
Phase 1 (2-3 hrs) ── Art pipeline ──→ Phase 3 (1-2 hrs) ──→ Phase 4 (30 min) → SHIPPED
                                      ↑
Phase 2 (30 min)   ── Gaze mechanic ──┘
```

Phase 2 can happen in parallel with Phase 1. Phase 3 depends on both Phase 1 (assets exist) and Phase 2 (mechanic defined). Phase 4 depends on Phase 3.

**Total estimated time: ~4-6 hours of actual work, mostly unattended generation time.**

---

## Success Criteria

- [ ] No corrupted files remaining
- [ ] All 6 base wall textures generated at PS5 quality, tileable
- [ ] Lacanian text rendered on 3+ texture variants
- [ ] Sprite textures generated or Canvas2D placeholders upgraded
- [ ] Deploy script works with one command
- [ ] Live site shows new quality at topherrasmussen.com/gaze.html
- [ ] Gaze mechanic documented in GAZE_MECHANIC.md
- [ ] Asset inventory complete with status tracking
