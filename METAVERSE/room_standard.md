# Room Standard — what goes where, how it works
2026-10-17 · Steven's directive: "whatever you see fit, you take over, tell me what you're putting in."

`doc-room.html` is the template. Every character room follows it.

## Entry flow
Dashboard (frame) → tap character panel → **onboarding ritual** → room fades in, character standing there, greets.

The ritual (taken from the Ellura UI — the best thing in it), FIRSTBREATH-worded:
- Stage 1 — SYNCHRONIZE: handshake with the room.
- Stage 2 — DIRECTIVES: the three laws.
  - [01] Information density balances continuously via CAG optimization.
  - [02] System memory uses real-world layering, never stacking.
  - [03] Symplectic integration maintains strict context integrity.
- Button: STEP INSIDE → overlay fades → greeting line in the speech cloud.

## The room substrate (the 360° standard)
Every room runs on the same engine:
- **Gyroscope** — yaw→width, pitch→height, roll→length. Drag orbits a full 360°.
- **Parallax layers** (6, far = smaller/dimmer/slower), world-locked sun glow, vignette, gimbal rings.
- **Cel-shaded figures** — 3-tone bands, ink outlines, blob shadows. Flat that pops.
- **Character behavior** — idle motion (Doc's frail sway, pivoting at the feet); faces the visitor (counter-rotates the world's yaw).

## What goes where
- **FRAME** (no connection into the room — observation without conduction): permanent icons (Don't Panic, previous-app, talk/text, audio, files, camera, calls), the 11-slot lineup, media (music, movies, videos — all outside).
- **ROOM INTERIOR**: the character, their domain objects, the speech cloud, the terminal stream.
- **Navigation feels like a building**: tap a panel → it opens → rooms inside → choose one → go deeper. The character guides: "we gotta go this way." Nested, not flat.

## Communication (per the dialogue doctrine)
- **Primary**: floating speech cloud above the character's head. Tap it (or them) to cycle their lines. Doc's 8 established lines from the dashboard mockup — no invented dialogue.
- **Secondary**: terminal stream (typewriter effect), with room-appropriate commands.
- **Input** (future): audio, talk-to-text, text.

## Room inventory
1. **Doc's Invention Box** — DONE. Empty room + Doc. (This file is the template.)
2. Whizapp's App Dev room — next.
3-7. B-Deal, Stan, Community Connections rooms, Panel 6, FIRSTBREATH Realm — per cast list.

## Room types (2026-10-17 — his grown vision)
- **Guide rooms** (Doc's): one visitor + the character. Learning, inventing, being shown things.
- **Co-creation rooms** (NEW): many people in the same area, teamwork — everyone watching the same idea come to fruition, everyone putting input right on the screen, all of it building ONE thing together. The room is a workshop, not a stage.
- The giving economy lives in the rooms: people doing things for people, points earned toward free stuff, donated apps, free rentals. The ONLY currency is doing good — nobody buys in; rewards are earned solely with volunteered personal time. No bullying, no bought status — nobody cares what Don's wearing, because Todd doesn't either.

## What was taken, what was put in (2026-10-17)
- TAKEN from `ellura-sovereign-substrate-ui.html`: the two-stage onboarding ritual (structure + three laws), the terminal-stream UX (log nodes, typewriter, command pattern).
- LEFT: three.js particle cloud (fights the parallax doctrine), mocked telemetry, CDN deps, "Lagrangian" name without the math.
- PUT INTO `doc-room.html`: onboarding overlay (FIRSTBREATH-worded), terminal stream drawer (help, /clear, /idea), Doc speech cloud (his 8 lines, tap-to-cycle, positioned above his head each frame).