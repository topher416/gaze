# The Gaze — Asset Inventory

## Wall Textures (1024×1024, tileable, PS5 etched)

| Asset | Source | Status | Size | Notes |
|-------|--------|--------|------|-------|
| stone_wall_tileable | SD 1.5 (new prompt) | ❌ generating | — | Regenerating with --tile prompts |
| stone_wall_alt_tileable | SD 1.5 (new prompt) | ❌ generating | — | Variation for visual diversity |
| mirror_wall_tileable | SD 1.5 (new prompt) | ❌ generating | — | Ornate cracked mirror pattern |
| door_wall_tileable | SD 1.5 (new prompt) | ❌ generating | — | Gothic door panel pattern |
| floor_stone_tileable | SD 1.5 (new prompt) | ❌ generating | — | Cobblestone floor |

## Legacy Wall Textures (256×256, Canvas2D placeholder)

| Asset | Status | Size | Notes |
|-------|--------|------|-------|
| genStone() | ✅ in code | ~8KB | Procedural Canvas2D, will be overridden by ComfyUI |
| genMirror() | ✅ in code | ~4KB | Procedural Canvas2D, will be overridden |
| genDoor() | ✅ in code | ~4KB | Procedural Canvas2D, will be overridden |

## Sprite Textures

| Asset | Size | Status | Notes |
|-------|------|--------|-------|
| enemy_reflection (4 states: idle/chase/pain/dead) | 512×512 each | ❌ pending | SD 1.5/Flux, needs generation |
| enemy_gaze_eye (4 states: idle/chase/pain/dead) | 512×512 each | ❌ pending | SD 1.5/Flux |
| enemy_mirror_frame (4 states: idle/chase/pain/dead) | 512×512 each | ❌ pending | SD 1.5/Flux |
| pickup_desire_orb | 256×256 | ❌ pending | SD 1.5/Flux or Canvas2D OK |

## Canvas2D Text Overlay (Lacanian quotes)

| Quote | Target Wall | Status | Notes |
|-------|-------------|--------|-------|
| "Je pense là où je ne suis pas" | stone_wall_tileable | ❌ pending | Canvas2D overlay at 30-50% opacity |
| "L'Autre" | mirror_wall_tileable | ❌ pending | Canvas2D overlay |
| "Désir de l'Autre" | door_wall_tileable | ❌ pending | Canvas2D overlay |
| "Le signifié flotte sous le signifiant" | stone_wall_alt | ❌ pending | Canvas2D overlay |

## L'Autre Special Sprites

| Asset | Size | Status | Notes |
|-------|------|--------|-------|
| l_autre_eye | 256×256 | ❌ pending | The Other — cannot be dissolved |

## Deployment

| Target | Repo | Status | Notes |
|--------|------|--------|-------|
| Raw GitHub | topher416/gaze | ✅ synced | 31,588 bytes |
| Live site | topherrasmussen.com/gaze.html | ✅ synced | 31,588 bytes |
