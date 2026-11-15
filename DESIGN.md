# STREET FIGHTER II': CHAMPION EDITION 80 — Design & Architecture

## 1. Visual Direction: NGPC Chibi Cabinet
- **Native Resolution**: `240x136` integer pixel grid (16-color `NGPC_SF2_16` custom RGB palette embedded in `CHUNK_PALETTE`, `0x3FC0`).
- **Palette Contract (`NGPC_SF2_16`)**:
  - `0`: `#141624` (Deep Ink Outline / BG Void)
  - `1`: `#F4F4F8` (Pure White / Ryu Gi / Flash)
  - `2`: `#C8CEE2` (Cool Silver / Gi Shade / Vega Claw)
  - `3`: `#5A627D` (Steel Slate / Concrete / Dark Metal)
  - `4`: `#FFC89C` (Light Skin)
  - `5`: `#D4885C` (Warm Tan / Skin Shadow)
  - `6`: `#6B3A28` (Mahogany / Hair / Wood / Balrog Skin)
  - `7`: `#E62E3D` (Arcade Crimson Red / Ken Gi / Ryu Band / HUD)
  - `8`: `#F58025` (Blazing Orange / Blanka Hair / Yoga Fire)
  - `9`: `#FFD93B` (Electric Gold / SF2 HP Yellow / Guile Hair)
  - `10`: `#52D660` (Emerald Green / Blanka Skin / Guile Camo)
  - `11`: `#1B7A44` (Deep Forest Green / Camo Shade / Jungle)
  - `12`: `#2C9CF5` (Arcade Sky Blue / Chun-Li Qipao / Sky)
  - `13`: `#1B3894` (Deep Cobalt / Royal Blue / Ryu 2P / Night)
  - `14`: `#6CF0FF` (Electric Cyan / Hadouken / Sonic Boom / Sparks)
  - `15`: `#882E96` (Psycho Purple / M.Bison / Vega Trim / Night)
- **Sprite Anatomy & Bounds**:
  - Chibi proportions (`36-40px` standing, `25-29px` crouching): 1px dark outline (`0`) around head (`14-16px` square-round), torso, and active limbs so reads stay instantaneous at 1x or 6x scale.
  - All `print()` text stays strictly within `[0..240] x [0..136]` bounds.

## 2. Combat Engine Architecture
- **Deterministic Fixed-Timestep**: Runs inside TIC-80 `60Hz` `TIC()` loop; `HF Turbo` applies `turbo_acc += 0.25` (1.25x cadence, 2 steps every 4th frame).
- **20-Frame Ring Input Buffer (`dir_buf`)**:
  - Normalized to facing-relative numpad directions (`1..9`: `6` = Forward, `4` = Back, `2` = Down, `8` = Up).
  - Supports **Negative Edge** (`inp.p[b]` OR `inp.r[b]` on button release) for reliable special execution.
  - Priority hierarchy: `360` SPD -> `623` DP -> `41236` Half-Circle -> `236` / `214` Quarter-Circle -> `[4]6` / `[2]8` Charge (with 12f charge partition grace window) -> Mash (`>=4` presses in 28f).
- **Authentic SF2 Collision & Recovery**:
  - Separate `hurtbox`, active `hitbox`, and body `pushbox` with corner pushback transfer (attacker pushed back on defender corner contact).
  - Normal -> Special Cancel window (`cancels` after hit/block contact during active/early recovery frames).
  - High / Low / Overhead / Cross-up blocking + Chip damage (`ceil(dmg * 0.2)` minimum 1 HP on specials/chips, non-lethal only where authentic or clearly tracked).
  - Dizzy / Stun meter (`stun` builds on unblocked hits, decays during neutral, triggers stars overhead on threshold with mash recovery).

## 3. Web Cockpit & Multi-Input Bridge
- **Direct Input Paths**:
  - **Keyboard**: Dispatched directly to TIC-80 (`Arrows + ZXAS` 1P, `IJKL + YNUH` / `O,./` 2P, `Space/Enter` Pause, `Tab` Hitboxes, `R` Guard toggle, `M` Mute). Web virtual controls forward pointer actions as synthetic `KeyboardEvent`s targeting `document` so keyboard and touch never diverge.
  - **HTML5 Gamepad**: Poll `navigator.getGamepads()` on `requestAnimationFrame` for up to 2 pads; map Axis/D-Pad + Face/Shoulder buttons (`X/Y/A/B/RB/RT`) to P1 (`Arrows+ZXAS`) and P2 (`IJKL+YNUH`) key events cleanly, updating live cockpit badges.
  - **Virtual Touch Controls (`AUTO / ON / OFF`)**:
    - Auto-activated when `(pointer: coarse)`, `maxTouchPoints > 0`, or first `touchstart`/`pointerType === 'touch'`.
    - **Left 8-way Arcade D-Pad**: Tracks center vector `(dx, dy)` using `atan2` divided into 8 sectors (`22.5°` half-width diagonals) so circular thumb slides cleanly produce `2 -> 3 -> 6` without lifting fingers.
    - **Right 4-Button Fight Pad**: Diamond arcade layout (`LP [Z]`, `HP [A]`, `LK [X]`, `HK [S]`) + rapid timed macro pills (`SP1` executes `2 -> 3 -> 6 -> LP`, `SP2` executes `6 -> 2 -> 3 -> HP` or `[4]->6+P` cleanly, `THROW` holds `6 + LP`).
- **Mobile & Tablet Responsive Ergonomics**:
  - Portrait guard (`#orientation-overlay`) protects playable aspect ratio and prompts landscape rotation (`Traditional Chinese + English`), offering native `screen.orientation.lock('landscape')` when allowed by user gesture plus a fallback dismiss control.
  - Landscape mobile tightens top bar to essential controls and fits D-Pad + CRT `240x136` + Fight Pad within `100dvh` with `touch-action: none` and `env(safe-area-inset-*)` padding.
