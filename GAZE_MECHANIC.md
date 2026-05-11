# The Gaze — Interaction Design Document

## Core Principle
**Looking is the action.** The player's attention transforms what is observed. Not violence — recognition.

## What "Looking At" Means

### The Gaze Cone
- Enemies have a **field-of-view arc** (60° cone, same as player's) — they can "look back"
- When an enemy is **both in the player's view AND the player is in the enemy's view** (mutual gaze), the interaction triggers
- Detection: enemy direction vs. player angle, distance < 8 units
- Duration threshold: **2 seconds** of sustained mutual gaze

### How It's Detected
```
// Each frame, for each enemy:
// 1. Is enemy in front of player? (within player FOV)
// 2. Is player in front of enemy? (within enemy's 60° cone)
// 3. Is distance < 8?
// If all three: mutualGaze = true, start/continue timer
// If mutualGaze held for 2s: trigger transformation
```

## What Happens When Observed

### Phase 1: Noticing (0–2 seconds)
- Enemy **stops moving** — it notices it's being watched
- Visual: enemy sprite flashes (brief red overlay, like "pain" but softer)
- Audio: low harmonic shift in the drone (+1 semitone for each gazed enemy)
- HUD: a subtle "being watched" indicator (the desire bar pulses)

### Phase 2: Recognition (2 seconds of sustained gaze)
- Enemy **transforms** — not dies, but changes state
- The reflection recognizes itself — the enemy sprite becomes translucent, starts dissolving
- **Desire is restored** (+15 per enemy recognized) — recognition feeds desire
- Audio: Tone.js resonance bloom (brief warm chord)
- The dissolved enemy leaves behind a **trace** — faint sprite that persists as background decoration, no longer threatening

### Phase 3: Looking Away (consequence)
- If the player **looks away** before 2 seconds (moves camera off enemy):
  - Enemy **resumes pursuit** with **increased speed** (1.5× original)
  - "You looked and turned away — it remembers"
  - Desire drains slightly (-5) — the guilt of broken attention
- If the player **never looked** at the enemy:
  - Enemy continues normal patrol speed
  - Enemy only drains Desire on contact (as before)

## The Central Mechanic: The Gaze Looks Back

### The Mirror Room
- At the center of the map, enemies spawn facing outward from a central point
- When the player reaches the center and looks at **all mirrors simultaneously** (a moment of full spatial awareness), something happens:
  - A special sprite appears — **L'Autre** (The Other)
  - It has no body, just an eye
  - It cannot be dissolved by looking — it *is* looking
  - Its presence drains Desire continuously while on screen
  - The only escape: run. You can't look it away.

### Why This Works Lacan-Wise
- The gaze is not what you see — it's **the point from which you are seen**
- Mutual reflection = the subject confronting its own split (imaginary vs. symbolic)
- Dissolution through sustained looking = the subject integrating rather than disavowing
- Looking away = the defensive gesture — "I saw something, now I refuse to keep seeing" → makes it stronger
- L'Autre = the Real — what can't be symbolized, only fled from

## Updated State Machine

```
idle → NOTICED (player gaze detected, stopped) 
       → DISSOLVING (2s mutual gaze sustained, +15 Desire)
       → GONE (trace sprite, non-threatening, no Desire drain)

NOTICED → CHASE_FASTER (player looked away, speed ×1.5, -5 Desire)

CHASING → NOTICED (player gazes it)

New enemy state: l'autre — always on screen, always watching, continuous drain
```

## Implementation Notes

### Direction Tracking for Enemies
Each enemy needs an `angle` property — the direction they face. When chasing: face player. When idle: slow rotation. When noticed: face player and hold.

### Mutual Gaze Check
```
// Player→enemy check
var enemyAngle = Math.atan2(player.y - sp.y, player.x - sp.x);
// Already have: ray angle for what player is looking at (center of screen = player.angle)
// Is enemy within player.viewCone (±30° from player.angle)?
// Is player within enemy.viewCone (±30° from sp.angle)?
```

### UI: The "Being Watched" Indicator
- Desire bar pulses when any enemy is actively gazing at the player (even without mutual gaze)
- When mutual gaze achieved: bar glows gold instead of rust-red
- Visual feedback that something is happening, not just "health goes down"

### No New Input Required
The player doesn't need to press a button to "look." **Movement + camera orientation is the look.** The mechanic emerges from navigation choices, not new controls.

## What This Means for v0.2.1

- Add `angle` and `gazeState` to each enemy
- Add mutualGaze detection to game loop
- Add dissolution animation (existing dead animation repurposed — but slower, more graceful, no contact needed)
- Add trace sprites for dissolved enemies
- Add L'Autre as special-case enemy (spawn event, not tile-based)
- Add audio cues for mutual gaze states
- Desire gain is the reward for looking — not violence for surviving

## Victory Condition
When **all 7 enemies are dissolved through gaze**, the labyrinth shifts — L'Autre appears. The player must reach the door (cell type 3 at bottom-right of map). Reaching it with Desire > 0: the gaze completes, you are seen by what sees you. Game ends with a Lacanian quote on screen. Death if Desire hits 0 before reaching the door.

## Quotes by State
- Title: "What sees you, sees itself seeing."
- Dissolution: "Le signifié flotte sous le signifiant"
- L'Autre appears: "L'inconscient est structuré comme un langage"
- Victory: "Je pense là où je ne suis pas"
- Death: "Tu ne veux rien savoir de ton désir"
