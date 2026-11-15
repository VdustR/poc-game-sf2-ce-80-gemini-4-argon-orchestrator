# STREET FIGHTER II': CHAMPION EDITION 80

**Neo Geo Pocket Color (*Match of the Millennium* SD/Chibi) Style Tribute to *Street Fighter II': Champion Edition* on the TIC-80 Fantasy Console (`240×136`)**

---

## Overview

`sf2-ce-80` (`v1.0.0`) is a fan tribute to Capcom's *Street Fighter II': Champion Edition* (1992) engineered for **TIC-80 v1.4.1** and packaged as an offline-ready Web PWA arcade shell. It combines CPS-1 fighting mechanics (hitstop, normal-to-special cancels, negative-edge inputs, 36 special moves, command normals, throws, stun/dizzy, mirror-match 2P palettes, and toggleable Hyper Fighting Turbo speed) with a 16-color Neo Geo Pocket Color chibi visual presentation.

### Highlights
- **Native TIC-80 v1.4.1 WebAssembly Execution**: Boots [sf2_ce_80.tic](sf2_ce_80.tic) inside the bundled `nesbox/TIC-80 v1.4.1` WASM runtime (`vendor/tic80/tic80.js` + `tic80lua.wasm`) with default `CRT: ON` scanlines and `INT: ON` integer scaling (`768×432` desktop / `512×288` mobile landscape for TIC-80's `256×144` overscan frame).
- **Full 12-Fighter Roster & 36 Special Moves**: `RYU`, `KEN`, `CHUN-LI`, `GUILE`, `BLANKA`, `E.HONDA`, `ZANGIEF`, `DHALSIM`, `BALROG`, `VEGA`, `SAGAT`, and `M.BISON`, each with 3 special moves, Champion Edition mirror-match alternate palettes, and signature animated stages.
- **Game Modes & Arcade Details**:
  - `1P ARCADE` ladder (Best-of-3 rounds, Stage 4 **Crush the Car Bonus Stage**, post-round `TIME` + `VITAL` score tally, 1-on-1 KO echo)
  - `2P VERSUS` (shared keyboard or dual HTML5 gamepads)
  - `TRAINING` (regenerating HP, live `Tab` hitbox viewer, `R` dummy guard toggle)
  - `CAR BONUS` standalone mode & `MOVE LIST` command reference
  - **3-Phase Arcade Opening Animation** (`title_idle < 115`) & 480-frame **Attract Mode**
- **8-Track, 48-Pattern Chiptune Soundtrack**: Authentic TIC-80 tracker transcriptions across Opening & Player Select, *Ryu's Theme*, *Guile's Theme*, *Chun-Li's Theme*, *Four Kings Boss Theme*, *Low-HP Pinch*, *VS / Bonus Stage*, and *Victory Fanfare*, plus 12 gameplay/UI SFX.
- **Adaptive Arcade Input**: Keyboard, HTML5 Gamepad (`auto P1/P2`), and automatic touch cockpit with portrait Rotate-to-Landscape guidance, an 8-way slide D-Pad, and `SP1`/`SP2`/`THROW` macros.

---

## Controls

| Action | 1P Keyboard | 2P Versus Keyboard | Gamepad / Touch Cockpit |
|---|---|---|---|
| **Move / Guard** | `Arrow Keys` | `I` / `J` / `K` / `L` | D-Pad / Analog Stick / 8-Way Touch D-Pad |
| **LP / LK** | `Z` / `X` | `Y` / `N` (or `,` / `.`) | Face `X` / `A` / Touch `LP` / `LK` |
| **HP / HK** | `A` / `S` (alt `U` / `J`) | `U` / `H` (or `O` / `/`) | Face `Y` / `B` / Touch `HP` / `HK` |
| **Start / Pause** | `Enter` / `Space` | — | Gamepad `Start` / Top Bar `PAUSE` |
| **Training Tools** | `Tab` (Hitboxes), `R` (Guard) | — | Header `MOVES` drawer |
| **Audio / Video** | `M` (Mute) | — | Top Bar `CRT`, `INT`, `AUDIO`, `FULL`, `RESET` |

---

## Repository Layout

- [build_tic.py](build_tic.py) — Cartridge synthesizer (`sf2_ce_80.lua` and binary `sf2_ce_80.tic` chunks: tiles, waveforms, SFX, music patterns/tracks, palette, compacted Lua)
- [verify_e2e.js](verify_e2e.js) — Binary chunk integrity verifier (including 1-based tracker pattern checks) and headless `luajit` simulation across all 12 fighters & 36 specials
- [web/template.html](web/template.html) — Self-contained HTML5/PWA arcade player shell & touch cockpit
- [public/](public/) — PWA manifest, service worker (`sw.js`), and pixel-art icons
- [scripts/](scripts/) — Build pipeline (`build.mjs`), static preview server (`serve-dist.mjs`), dist smoke test (`smoke-test.mjs`), and Playwright player suite (`verify-player.mjs`)
- [vendor/tic80/](vendor/tic80/) — Official TIC-80 v1.4.1 WASM player assets
- [PRODUCT.md](PRODUCT.md) & [DESIGN.md](DESIGN.md) — Product & design specifications
- [docs/](docs/) — Research notes and iterative optimization log

---

## Build & Verification

Prerequisites: `python3`, `luajit`, and `node` (`npm install`).

```bash
# 1. Regenerate sf2_ce_80.lua & sf2_ce_80.tic and build dist/ + dist/sf2-ce-80-web.zip
npm run build

# 2. Run binary + LuaJIT mechanics E2E, dist smoke check, and Playwright desktop/mobile suite
npm test

# 3. Serve the built PWA locally (default port 4173)
npm run serve
```
