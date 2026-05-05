# The Gaze

A DOOM-style raycaster with Lacanian themes. Navigate a labyrinth of theater rooms, encountering mirrors, reflections, and the Gaze.

## Features

- **Raycaster engine** — DDA raycasting at 640×400 resolution
- **Etched textures** — Procedurally generated stone, mirror, and door walls with Lacanian text (THE SYMBOLIC, THE IMAGINARY, THE REAL, etc.)
- **Distance shading** — Walls darken with distance, side faces cast shadows
- **Collision detection** — Wall-sliding movement prevents clipping

## Play

Open `index.html` in a browser.
- **WASD** — Move
- **Arrow keys** — Move (alternatively)
- **Mouse** — Look around (click canvas to lock pointer)

## Tech

- Single HTML file, no build step
- No external assets — all textures generated procedurally via Canvas 2D
- Vanilla JavaScript, no dependencies
- Canvas 2D rendering (no WebGL)

## Status

**v0.1** — Skeleton release. Walls, movement, collision. Sprites, enemies, audio, and gameplay coming in 0.2.
