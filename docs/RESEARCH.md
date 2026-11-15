# Research Foundation — STREET FIGHTER II': CHAMPION EDITION 80

This document records the per-topic technical and design research conducted prior to implementation.

---

## Topic 1 — Classic Version Identity: *Street Fighter II': Champion Edition* (1992) + *Hyper Fighting* Speed Option

- **Why Champion Edition (`SF2' CE` / `Dash`) is the definitive classic version**:
  - Retains the original *World Warrior* visual and audio identity while unlocking all **12 iconic fighters** (the 8 World Warriors + the 4 Grand Masters: Balrog, Vega, Sagat, M. Bison) and **mirror matches** with distinct 1P/2P color schemes.
  - Features the classic 12-stage world tour and the **Crush the Car Bonus Stage** after early tournament matches.
  - Provides balanced, readable neutral footsies, projectile zoning, anti-air Shoryuken/Flash Kick punishes, and normal-to-special cancels without Super Meter complexity.
- **Hyper Fighting (`HF`) Speed Mode**:
  - Players can toggle `CE NORMAL` (1.0x classic pacing) or `HF TURBO` (faster frame advance / snappier startup & recovery) right on the Title screen, plus Ryu/Ken's iconic **Air Hurricane Kick** (`214+K` in mid-air) and Chun-Li's **Kikoken** (`[4]6+P`) which complete their classic moveset expectations.

---

## Topic 2 — Neo Geo Pocket Color (*Match of the Millennium*) Art & Palette Architecture

- **Display Constraints**: TIC-80 native resolution is `240x136` (`16:9`) with a 16-color master palette (`CHUNK_PALETTE`) and 8x8 tile memory (`CHUNK_TILES`).
- **NGPC Chibi Proportions**:
  - Standing fighter height: `36px–40px` (~28% of screen height), leaving spacious horizontal footsies across a `320px`-wide scrolling stage (`cam_x` in `0..80`).
  - Ratio: `16x16` expressive head (~42% of height) with distinct headwear/hair silhouettes (`Ryu/Ken headband`, `Chun-Li ox-horn buns`, `Guile flattop`, `Blanka wild orange mane`, `E.Honda kabuki kumadori`, `Zangief mohawk + beard`, `Dhalsim skull necklace`, `Balrog fade + boxing gloves`, `Vega mask + steel claw`, `Sagat eyepatch + chest scar`, `M.Bison peaked military cap + cape`).
  - **1px Dark Ink Outline (`#1a1c2c`, index 0)** on every body segment and projectile so sprites stay crisp against all 12 brightly colored stages.
- **16-Color Master Palette (`NGPC_SF2_16`) & 1P/2P Remapping**:
  - Designed to simultaneously carry SF2's iconic **Yellow (`#ffd93b`) / Red (`#e62e3d`)** vitality HUD, crisp white/silver highlights, skin tones, and all 12 fighters' 1P and 2P Champion Edition color palettes.
  - Sprite tiles (projectiles, sparks, dizzy icons, car parts) use TIC-80's hardware palette remap register (`0x3FF0`, `poke4(0x3FF0*2 + src, dst)`) to swap projectile tints per fighter (`Hadouken` cyan vs `Tiger Shot` gold vs `Yoga Fire` orange).

---

## Topic 3 — Authentic SF2 Combat Engine, Frame Data & Physics

- **60Hz Fixed-Step Simulation**:
  - `CE NORMAL`: 1 simulation tick per frame (60Hz).
  - `HF TURBO`: Accumulates `1.25` simulation steps per frame (every 4th frame steps twice) for authentic turbo responsiveness without breaking 1-frame input sampling.
- **3-Frame Pre-Jump Squat & Committed Jump Arcs**:
  - Pressing `Up` enters `STATE_PREJUMP` for 3 frames (throw-invulnerable on frames 2–3), then launches into a deterministic parabolic jump (`Neutral`, `Forward`, or `Backward` locked at takeoff, `vy0 = -4.2`, `g = 0.23`).
- **Hitstop (Hit-Freeze)**:
  - Light attacks: `6` frames; Medium/Heavy attacks: `9` frames; Special moves: `11` frames.
  - Both fighters pause animation/movement during hitstop while **motion input buffering remains active**, enabling hit-confirm cancels (e.g., `cr.LK / cr.HK -> Hadouken / Shoryuken`).
- **Normal-to-Special Cancel Window**:
  - Grounded cancelable normals (`LP`, `HP`, `LK`, `CR_P`, `CR_K`) allow canceling directly into any valid special move from the first hit/active frame through hitstop and early recovery.
- **High / Low / Overhead / Throw Matrix**:
  - Standing attacks hit `Mid` (blocked by Stand or Crouch Guard).
  - Crouching kicks (`CR_K`) hit `Low` (must be Crouch Blocked with `Down-Back`; beats Stand Guard).
  - Jumping normals (`AIR_P`, `AIR_K`) hit `Overhead` (must be Stand Blocked with `Back`; beats Crouch Guard).
  - Cross-up air attacks switch the attacker's relative side, reversing which direction is `Back` for the defender.
  - Special moves deal **Chip Damage** (`2..4` HP) on block; normals deal `0` chip damage.
  - **Close Throws (`Forward/Back + HP/HK` or `LP+LK` within `24px`)** beat standing and crouching guard, ignore blockstun, and throw/knockdown the opponent unless the defender is airborne, in hitstun, or in pre-jump throw invulnerability.
- **3-Box Collision & Corner Pushback Transfer**:
  - `Pushbox` keeps fighters separated (`min_sep = 16px`), allowing cross-ups when one fighter is sufficiently above the other (`dy > 18px`).
  - `Hurtbox` (shrinks vertically on crouch) and `Hitbox` resolve trades simultaneously when both hitboxes overlap on the same frame.
  - When a hit or block applies horizontal pushback and the defender is pinned at a stage wall (`x <= 18` or `x >= 302`), the remaining pushback **transfers backward onto the attacker**, recreating SF2's signature corner spacing.
- **Dizzy / Stun System**:
  - Every hit adds stun damage (`8..22`); stun decays slowly after `120` idle frames.
  - Crossing `100` stun triggers `STATE_DIZZY` (`150` frames base) with animated spinning stars/birds above the head. Rapid directional wiggling + button presses decrement `dizzy_t` by `3` frames per input edge, matching classic SF2 mash recovery.

---

## Topic 4 — Complete 12-Fighter Roster & Special Move Specification

| # | Fighter | Archetype | Walk F/B | Special 1 | Special 2 | Special 3 |
|---|---------|-----------|----------|-----------|-----------|-----------|
| 1 | **RYU** | Shoto All-Rounder | 1.35 / 1.15 | Hadouken (`236+P`) | Shoryuken (`623+P`, air/invuln startup) | Tatsumaki (`214+K`, ground & air, proj-invuln) |
| 2 | **KEN** | Rushdown Shoto | 1.45 / 1.20 | Hadouken (`236+P`) | Shoryuken (`623+P`, multi-hit fiery arc) | Tatsumaki (`214+K`, faster horizontal spin) |
| 3 | **CHUN-LI** | High-Speed Striker | 1.75 / 1.50 | Kikoken (`[4]6+P`) | Hyakuretsukyaku (Mash `K` or `236+K`) | Spinning Bird Kick (`[2]8+K`) |
| 4 | **GUILE** | Charge Zoner | 1.30 / 1.15 | Sonic Boom (`[4]6+P`, fast recovery) | Flash Kick (`[2]8+K`, huge anti-air arc) | Spinning Backfist (`214+P`) |
| 5 | **BLANKA** | Wild Beast | 1.40 / 1.20 | Rolling Attack (`[4]6+P`) | Electric Thunder (Mash `P` or `214+P`) | Vertical Roll (`[2]8+K`) |
| 6 | **E.HONDA** | Sumo Bruiser | 1.05 / 0.90 | Hundred Hand Slap (Mash `P` or `236+P`) | Sumo Headbutt (`[4]6+P`) | Sumo Smash (`[2]8+K`) |
| 7 | **ZANGIEF** | Heavy Grappler | 0.90 / 0.78 | Screw Piledriver (`360+P` high-dmg grab) | Double Lariat (`HP+HK` or `236+P`, anti-proj) | Siberian Bear (`214+K` lunging slam) |
| 8 | **DHALSIM** | Long-Limb Zoner | 0.88 / 0.75 | Yoga Fire (`236+P`) | Yoga Flame (`41236+P` or `214+P`) | Yoga Teleport (`623+K` / `421+K` / `HP+HK`) |
| 9 | **BALROG** | Rush Boxer | 1.42 / 1.22 | Dash Straight (`[4]6+P`) | Dash Upper (`[4]6+K`) | Buffalo Headbutt (`[2]8+P/K`) |
| 10 | **VEGA** | Agile Assassin | 1.72 / 1.55 | Rolling Crystal Flash (`[4]6+P`) | Flying Barcelona (`[2]8+K`, wall/sky dive) | Scarlet Terror (`[2]8+P` / `214+K`) |
| 11 | **SAGAT** | Muay Thai Emperor | 1.18 / 1.00 | High/Low Tiger Shot (`236+P/K`) | Tiger Uppercut (`623+P`) | Tiger Knee (`236+K` / `214+K`) |
| 12 | **M.BISON** | Psycho Boss | 1.50 / 1.30 | Psycho Crusher (`[4]6+P`, multi-hit) | Double Knee Press (`[4]6+K`) | Head Press (`[2]8+K`) |

*(Note: Long-range normals on Dhalsim stretch limbs visually and extend hitboxes to `48px` while maintaining SF2's extended limb hurtbox balance.)*

---

## Topic 5 — Motion Input Ring Buffer, Negative Edge & Ergonomics

- **TIC-80 Hardware Constraint**: Each virtual gamepad exposes 8 bits (`0: Up, 1: Down, 2: Left, 3: Right, 4..7: 4 Action Buttons`).
- **4-Button Arcade Mapping + Optional NGPC Tap/Hold**:
  - `btn(4)` (`Z` / `J`): **LP** (Light Punch)
  - `btn(5)` (`X` / `K`): **LK** (Light Kick)
  - `btn(6)` (`A` / `U`): **HP** (Heavy Punch)
  - `btn(7)` (`S` / `I`): **HK** (Heavy Kick)
  - **2P Local Keyboard Mapping** via TIC-80 `key()` codes:
    - `I/K/J/L` (`9, 11, 10, 12`) for 2P Directions (Wait: `I=9, J=10, K=11, L=12` -> let's map `I=Up(9), K=Down(11), J=Left(10), L=Right(12)`!) and `U(21), O(15), Y(25), P(16)` or Numpad/Comma/Period/Slash (`45, 46, 47, 50`)! Let's verify exact indices from `src/tic.h`!
- **16-Frame Relative Direction Ring Buffer**:
  - Every frame records the player's direction translated relative to `facing` (`1..9` numpad notation, where `6` is always Forward and `4` is always Back).
  - **Negative Edge**: Trigger checks match both `just_pressed` (`btnp`) and `just_released` (`btnr`, held at least `3` frames and released within `6` frames of finishing a motion), making combo cancels like `cr.HP -> Shoryuken` feel crisp.
  - **Command Priority**: `360° (SPD)` > `623 (Dragon Punch)` > `236 / 214 (Quarter Circle)` > `Charge ([4]6 / [2]8)` > `Mash (4 taps)` > `Close Throw` > `Normals`.
  - **10-Frame Charge Partition Buffer**: When holding Back (`1/4/7`) or Down (`1/2/3`) for `>= 40` frames, releasing charge preserves `charge_ready` for `10` frames so players can transition cleanly into `Forward + P` or `Up + K`.

---

## Topic 6 — TIC-80 Audio Synthesis

- **Custom Waveforms (`CHUNK_WAVEFORM`)**: `0` = LFSR White Noise (hit/explosion/footsteps), `1` = 50% Square (arcade synth), `2` = Triangle (bass/chimes), `3` = Sawtooth (aggressive leads & brass), `4` = 25% Pulse (CPS-1 style brass/lead), `5` = Organ/Sub-harmonic.
- **16 Sound Effects (`CHUNK_SAMPLES`)**: Distinct synthesized SFX for Light Hit, Heavy Hit, Block Clank, Whiff Whoosh, Fireball Launch, Dragon Punch Rising, Throw Slam, KO Explosion (`"K.O.!"` impact), Menu Cursor, Confirm Coin, Round Start Bell, Dizzy Chirp, Car Smash Metal Crunch.
- **4-Channel Tracker Music (`CHUNK_PATTERNS`, `CHUNK_MUSIC`)**:
  - Track `0`: Title / Character Select energetic CPS-1 FM-style chiptune loop.
  - Track `1`: Main Fight Theme (high-tempo minor arcade rock riff with driving bassline and snare/kick).
  - Track `2`: Low-HP / Final Boss Pinch Theme (faster urgent modulation).
  - Track `3`: Victory / Car Bonus Fanfare.

---

## Topic 7 — Web Shell UX: Keyboard, Gamepad, Touch Auto-Detection & Landscape Prompt

- **Zero-Friction Official WASM Execution**: Loads `sf2_ce_80.tic` via `tic80.js` + `tic80lua.wasm` (`TIC-80 v1.4.1`) with zero external CDNs.
- **Multi-Input Auto-Detection & Bridging**:
  - **Keyboard**: 1P (`Arrows` or `WASD` + `Z/X/A/S` or `J/K/U/I` + `Space` Start) and 2P (`I/J/K/L` + `N/M/,/.` or `7/8/9/0`).
  - **Gamepad**: Uses both native Emscripten HTML5 Gamepad forwarding and a live 60Hz Web Shell Gamepad HUD indicator so connected USB/Bluetooth arcade sticks & pads show live status and work immediately.
  - **Virtual Touch Controls**: Auto-detected via `(pointer: coarse)`, `navigator.maxTouchPoints > 0`, or first `touchstart` event (`body.is-touch-active`), plus manual header toggle (`TOUCH: AUTO / ON / OFF`) so desktop testers can also toggle the virtual arcade stick at will.
  - **8-Way Slide-to-Motion D-Pad**: `22.5°`-accurate sector segmentation (`-22.5..22.5` Right, `22.5..67.5` Down-Right, `67.5..112.5` Down, etc.) with crisp diagonal feedback so rolling thumb from Down -> Down-Forward -> Forward executes Hadouken (`236`) and Forward -> Down -> Down-Forward executes Shoryuken (`623`) reliably!
  - **Multi-Touch Pointer Ownership**: Each touch pointer ID is tracked independently so sliding on the D-Pad (`pointerId A`) while tapping/holding `LP`/`HP`/`LK`/`HK` (`pointerId B`) never cancels held directions or blocks.
- **Mobile & Tablet Portrait-to-Landscape Prompt (`#orientation-overlay`)**:
  - Uses CSS media query + JS viewport/coarse-pointer detection (`isTouchDevice && window.innerHeight > window.innerWidth && window.innerWidth <= 1024`).
  - Displays a non-destructive, high-contrast prompt in Traditional Chinese & English (`請將手機或平板旋轉為橫向 / ROTATE TO LANDSCAPE`) showing a visual phone-rotation diagram, a one-tap `"進入橫向全螢幕 / LANDSCAPE FULLSCREEN"` button (using `requestFullscreen()` + `screen.orientation.lock('landscape')` with graceful fallback), and `"仍以直向繼續 / CONTINUE IN PORTRAIT"` dismissal persisted for the session.
- **Landscape Cockpit Layout**:
  - On mobile/tablet landscape (`orientation: landscape` and `max-height: 560px`) or Fullscreen Play Mode (`F`), uses a 3-column cockpit grid (`Left 8-Way D-Pad | Maximized 16:9 CRT Canvas | Right 4-Button Fight Pad + SP1/SP2/Throw Quick Triggers`) with `env(safe-area-inset-*)` padding for notched phones and `100dvh` overflow-free fit.

---

## Topic 8 — Strict Verification & Third-Party Exclusion Contract

- **Third-Party Components Excluded from Redundant Acceptance**: `nesbox/TIC-80 v1.4.1` WebAssembly core (`tic80.js`, `tic80lua.wasm`) browser/Emscripten/WebGL-loss/Service-Worker plumbing is already upstream-verified and excluded from fault-injection tests.
- **Strict Acceptance Scope for `sf2-ce-80`**:
  1. Binary `.tic` cartridge integrity (`CHUNK_CODE < 65535`, all audio/tile/palette chunks present).
  2. Complete 12-fighter verification in headless `luajit`: every fighter spawns, walks, crouches, jumps, blocks, throws, and executes all 3 special moves with valid hitboxes/projectiles and damage.
  3. SF2 Combat Engine invariants: Hitstop, Normal->Special Cancel combo, High/Low/Overhead guard rules, Chip damage, Throw vs Block, Corner pushback transfer, Dizzy trigger & mash recovery, Car Bonus Stage destruction, Idle Attract Mode (`480f`, no `pmem` pollution, exits on button press), and strict `240x136` UI text bounds.
  4. Real Web WASM E2E (`Playwright` + Chromium): Title -> Mode -> Character Select (12 fighters) -> Fight HUD, Keyboard controls, Gamepad indicator/bridge, Virtual Touch auto-detection & 8-way motion slide (`↓↘→ + LP`), and Mobile Portrait-to-Landscape prompt (`390x844` visible -> `844x390` hidden + cockpit layout).
