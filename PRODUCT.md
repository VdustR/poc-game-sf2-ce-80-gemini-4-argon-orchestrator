# STREET FIGHTER II': CHAMPION EDITION 80 — Product Specification

## 1. Identity & Tribute Scope
- **Title**: `STREET FIGHTER II': CHAMPION EDITION 80` (`sf2-ce-80`)
- **Platform**: TIC-80 v1.4.1 (240x136 16-color fantasy console) deployed primarily to Web via official TIC-80 WASM + custom Responsive Arcade Cockpit PWA.
- **Direct Tribute**: Authentic tribute to Capcom's *Street Fighter II': Champion Edition* (1992) with selectable **Champion (`CE`)** and **Hyper Fighting (`HF` Turbo)** game speeds. All 12 original World Warriors & Shadaloo Bosses retain their canonical names, stages, silhouettes, special moves, and Champion Edition mirror-match 2P palette swaps.
- **Visual Tribute**: Proportions, thick 1px ink outlines (`color 0`), expressive heads, and crisp high-contrast arcade HUD inspired by *SNK vs. Capcom: The Match of the Millennium* (Neo Geo Pocket Color).

## 2. Full 12-Character Roster
1. **RYU** (Suzaku Castle, Japan): Hadouken (`236+P`), Shoryuken (`623+P`), Tatsumaki (`214+K`).
2. **KEN** (Harbor Dock, USA): Hadouken (`236+P`), Flame Shoryuken (`623+P`), Tatsumaki (`214+K`).
3. **CHUN-LI** (Shopping Street, China): Kikoken (`[4]6+P`), Lightning Legs (`Mash K`), Spinning Bird Kick (`[2]8+K`).
4. **GUILE** (Air Force Base, USA): Sonic Boom (`[4]6+P`), Flash Kick (`[2]8+K`), Spinning Backfist / Air Throw.
5. **BLANKA** (Amazon River, Brazil): Electric Thunder (`Mash P`), Rolling Attack (`[4]6+P`), Vertical Roll (`[2]8+K`).
6. **E.HONDA** (Bathhouse, Japan): Hundred Hand Slap (`Mash P`), Sumo Headbutt (`[4]6+P`), Sumo Splash (`[2]8+K`).
7. **ZANGIEF** (Steel Works, USSR): Spinning Lariat (`LP+HP`), Spinning Piledriver (`360+P`), Atomic Suplex (`Close 4/6+P`).
8. **DHALSIM** (Maharaja Temple, India): Yoga Fire (`236+P`), Yoga Flame (`41236+P`), Yoga Drill (`Air 2+K`).
9. **BALROG** (Las Vegas Strip, USA): Dash Straight (`[4]6+P`), Dash Upper (`[4]6+K`), Turn Punch (`Hold P/K`).
10. **VEGA** (Meson Casino, Spain): Rolling Crystal Flash (`[4]6+P`), Sky High Claw (`[2]8+K`), Flying Barcelona (`[2]8+P`).
11. **SAGAT** (Ayutthaya Ruins, Thailand): Tiger Shot High (`236+P`), Tiger Shot Low (`236+K`), Tiger Uppercut (`623+P`).
12. **M.BISON** (Shadaloo Base, Thailand): Psycho Crusher (`[4]6+P`), Scissor Kick (`[4]6+K`), Head Press (`[2]8+K`).

## 3. Core Game Modes & Gameplay Systems
- **1P ARCADE**: Ladder progression with Mirror Matches allowed, Best-of-3 rounds, 99s CPS-1 timer, and **Crush the Car Bonus Stage** (Stage 4 / selectable directly on Title).
- **2P VERSUS**: Shared-keyboard (P1 Arrows+ZXAS vs P2 IJKL+YNUH / O,./) and Dual Gamepad support, Champion Edition Mirror Match 2P alt palettes.
- **TRAINING**: Regenerating HP, live Hitbox (`Hurt/Hit/Push`) overlay (`TAB`), and Guard toggle (`R`: None / Stand / Crouch-Auto).
- **CAR BONUS**: 20-second timed Bonus Stage smashing a destructible sedan with progressive denting, smoke, and wheel damage.
- **ATTRACT MODE**: Automated 480-frame idle demo on Title screen with clean exit on any human input and zero persistent score pollution.

## 4. Input & Web Delivery Experience
- **Desktop**: Keyboard + HTML5 Gamepad (single or dual controller) + optional on-screen touch/mouse test pad + collapsible 12-fighter Move List below the fold.
- **Mobile & Tablet**:
  - **Portrait Mode** (`height > width` on coarse-pointer or viewport `<= 1024px`): Full-bleed Rotate-to-Landscape prompt (`請將手機或平板旋轉為橫向 / ROTATE TO LANDSCAPE`) with one-tap Fullscreen+Landscape trigger and a session-dismissable `"CONTINUE"` option.
  - **Landscape Mode**: Maximized `240x136` CRT stage flanked by an 8-way slide-to-motion D-Pad on the left and ergonomic 4-button Arcade Fight Pad (`LP/LK/HP/HK`) + 1-tap `SP1`/`SP2`/`THROW` macros + live Input History Strip.
- **Offline First**: Zero external CDNs; all TIC-80 WASM files, PWA icons, and service worker bundle cleanly inside `dist/`.
