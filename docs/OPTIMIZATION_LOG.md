# Continuous Optimization Log — STREET FIGHTER II': CHAMPION EDITION 80

Each pass targeted a concrete gameplay, visual, or platform ergonomics bottleneck, followed by rebuilding `sf2_ce_80.tic` + `dist/` and verifying via `verify_e2e.js`, `scripts/smoke-test.mjs`, and `scripts/verify-player.mjs`.

## Pass 1 — Input Responsiveness, Charge Partition & Hitstop Cancel Buffering
- **Problem**: Headless E2E exposed three feel bottlenecks: (1) 38f charge was stiff on touchscreen D-Pads and lacked fast `[4]6`/`[2]8` responsiveness, (2) rapid-mash specials (`Lightning Legs`, `Electric Thunder`, `Hundred Hand Slap`) were blocked when a normal punch/kick started on tap 1 and whiffed or froze in hitstop, and (3) pressing `Up` (`7/8/9`) on the same frame as an upward special (`[2]8+K`, `360+P`) entered `FS_PREJUMP` before checking special commands.
- **Optimization**:
  - Tuned charge hold threshold from `38f` to `32f` with a `14f` charge-partition buffer (`chg_b_keep`, `chg_d_keep`).
  - Added 6-frame attack buffer (`buf_btn`, `buf_btn_t`) and immediate mash-cancel / hitstop-cancel handling in `step_fight()` and `FS_ATTACK`.
  - Evaluated `check_special_cmd()` on `dir >= 7` transitions and inside `FS_PREJUMP`.
  - Added `323` crouching Shoryuken / Tiger Uppercut leniency (`match_seq(buf, {3,2,3}, 14)`).
  - Tuned `M.BISON` `SCISSOR KICK` arc (`su=5, act=20, vx=3.2, vy=-2.5`) so mid-screen hits connect cleanly without premature landing.
- **Verification**: All 12 fighters x 3 specials (36 moves), normal->special cancel combo, and dizzy mash pass cleanly in `verify_e2e.js`.

## Pass 2 — Combat Impact, Hitflash, Energy Trails & K.O. Drama
- **Problem**: Hits during brisk Hyper Fighting matches needed stronger visual confirmation without increasing clutter.
- **Optimization**:
  - Added 3-frame white/cyan palette hitflash (`FS_HIT` `st_t <= 3`) using TIC-80 hardware palette remap (`0x3FF0`).
  - Added periodic cyan/orange spark trail particles behind flying Hadoukens, Kikokens, Sonic Booms, Yoga Fires, and Tiger Shots.
  - Added dramatic K.O. half-speed cadence (`t%2==1` step skip when `P1.hp<=0` or `P2.hp<=0`).
  - Widened corner pushback detection radius from `20px` to `24px` (`STG_W-24`) so cornered combos reliably push attackers outward.

## Pass 3 — Unified NGPC Chibi Expressive Faces & Portrait Readability
- **Problem**: Visual inspection of rendered PNGs (`02-desktop-fight.png`, `03-touch-slide-motion.png`) revealed blank circular portraits on HUD/Select/VS screens and low contrast where yellow character names overlapped white portrait backgrounds (`RYU`).
- **Optimization**:
  - Extracted shared `draw_chibi_head(cid, sx, cy, dir, p, r, anim)` renderer drawing expressive sclera + pupils + angled brows + all 12 signature head/hair/accessory motifs (Ryu animated headband, Ken blonde pomp, Chun-Li ox-horn buns with gold trim, Guile flat-top, Blanka feral mane, Honda kumadori streaks & topknot, Zangief mohawk & beard, Dhalsim skull marks, Balrog brow guard, Vega Venetian mask, Sagat eyepatch, M.Bison winged peaked cap).
  - Rendered high-contrast dark ink nameplates behind text on Select cards and VS portraits.

## Pass 4 — Stage Parallax, Expressive Spectators & Car Bonus Damage Progression
- **Problem**: Static castle silhouettes, blank spectator heads, and minimal car destruction phases reduced arcade atmosphere.
- **Optimization**:
  - Enriched Suzaku Castle with warm layered twilight bands, temple lantern/cloud silhouettes, eaves trim, and Shadaloo pulsing emblem.
  - Added cheering arm animations, hair bands, and eyes to stage spectators.
  - Added progressive shatter sparks, broken windshield glass fragments, dark smoke plumes (`hp < 45`), and bouncing detached tire (`hp < 35`) to `draw_car_bonus()`.

## Pass 5 — Mobile Landscape Cockpit Containment & Bidirectional Touch Macros
- **Problem**: Screenshot `06-mobile-landscape-cockpit.png` revealed `.crt-bezel` slightly overflowing horizontally/vertically into the right macro pills and `.telemetry-strip` on `844x390` viewports, and touchscreen 1-tap macros assumed left-side facing (`→`).
- **Optimization**:
  - Constrained `@media (orientation: landscape) and (max-height: 540px)` `.crt-column` (`flex: 1 1 0%; min-width: 0`) and `.crt-bezel` (`width: 100%; max-width: calc((100dvh - 88px) * 240 / 136); max-height: calc(100dvh - 88px)`) with zero bezel/deck/telemetry overlap; hid non-essential `MOVES` button on short landscape viewports.
  - Added `#canvas { cursor: none; }` and bidirectional `#macro-flip` (`DIR:→` / `DIR:←`) control above the right-side fight buttons.
  - Updated `verify-player.mjs` to wait past the 2-second TIC-80 WASM splash (`2400ms`), verify `.crt-bezel` non-overlap strictly against both decks and telemetry strip, and capture all 6 desktop + mobile screenshots.

## Pass 6 — NGPC Hardware 256-Tile Sprite Sheet Architecture (`CHUNK_TILES`)
- **Problem**: Previous procedural vector rendering (`rect`/`circ`/`tri`) lacked the crisp pixel-art clusters, outlines, and dithered shading of Neo Geo Pocket Color (*SNK vs. Capcom: Match of the Millennium*).
- **Optimization**:
  - Replaced procedural character parts with a dedicated 256-tile `8×8` bitmap bank (`CHUNK_TILES`, 8,192B) in `build_tic.py`: 12 bespoke `16×16` fighter heads (`32..70`), 13 universal palette-remappable `24×16` body poses (`96..198`), `16×16` projectiles/FX/crates/spectators (`72..78`, `202..206`, `236`), and `48×16` intact & wrecked Bonus Sedan (`224`, `230`).
  - Added Bayer dithered sky horizon seams, roof shingle tiles, brick masonry, cherry blossom sprites, and animated ocean waves.
  - Bumped Service Worker cache strategy in `public/sw.js` to network-first.

## Pass 7 — Lua Code Minifier (`CHUNK_CODE`) & Authentic LP/HP Fireball Speed Separation
- **Problem**: `CHUNK_CODE` reached 61,614B out of 65,535B, and `SP_TBL` overloaded `hs` for both melee hitstop and heavy projectile velocity.
- **Optimization**:
  - Added quote-aware tokenizer `_minify_lua_line()` inside `compact_lua_for_tic()` to strip redundant operator/delimiter whitespace without touching strings, freeing ~3 KB of cartridge code budget.
  - Separated `hspd` (heavy projectile speed) from `hs` (hitstop) across Ryu, Ken, Chun-Li, Guile, Dhalsim, and Sagat fireballs (`spd` 1.40–1.85 vs `hspd` 2.15–2.85), restoring authentic LP slow vs HP fast fireball zoning.

## Pass 8 — Command Normals, Arcade Callouts & Active Limb/Aura Extensions
- **Problem**: Standard punches/kicks lacked extending fist/boot sprites up to `atk.reach`, hit states lacked comic facial expressions, and command normals/combat callouts were absent.
- **Optimization**:
  - Added Command Normals (`F+LP` Overhead/Headbutt for Ryu, Ken, E.Honda, Zangief; Guile `F+LK` Knee Kick; Chun-Li Air `D+LK` bounce Head Stomp) and arcade callout popups + score bonuses (`1ST ATTACK!`, `COUNTER!`, `CROSS-UP!`, `REVERSAL!`).
  - Added comic `><` pain-eye overlays during `FS_HIT`/`FS_DIZZY`, universal extending fist/glove/boot visuals matching `atk.reach`, Guile Flash Kick golden crescent (`spr(74)`), vortex rings for Hurricane/Spinning Bird/Scissor Kicks, and throw slam shockwaves.

## Pass 9 — High-Contrast HUD, Stun Gauge, National Flags & 5-Track Chiptune BGM
- **Problem**: White/cyan HUD names and scores lost contrast over bright stage skies; stun buildup had no visible gauge; Select/VS screens lacked country flags; Victory/Car Bonus needed dedicated music tracks.
- **Optimization**:
  - Wrapped fighter names, `SCORE`, `TRAINING`, and `timer_sec` in ink-bordered HUD panels, added real-time Stun/Dizzy warning bars and high-contrast `N HIT!` combo badges.
  - Implemented `draw_flag(cid, x, y)` rendering authentic `12×8` national flags for all 8 represented countries on Character Select and VS screens.
  - Expanded `build_music()` patterns `7..9` and added Track 3 (Victory Fanfare) and Track 4 (Bonus Stage upbeat theme).

## Pass 10 & 11 — Web Cabinet CRT Toggle, Style-Filtered Roster & Expanded E2E
- **Optimization**:
  - Added `#btn-crt` (`CRT: ON/OFF`) pure-CSS scanline/vignette overlay on `.crt-bezel` (leaving raw `#canvas` pixels clean), style filter pills (`ALL`, `MOTION`, `CHARGE`, `GRAPPLER / TECH`, `4 KINGS`) in `#roster-grid`, and bumped `public/sw.js` to `'sf2-ce-80-v3'`.
  - Expanded `verify_e2e.js` to validate minified `.tic` chunk 5 Lua syntax in `luajit`, LP vs HP fireball velocity separation, and Ryu `6+LP` Overhead guard-break; expanded `verify-player.mjs` to verify `#btn-crt` and capture `09-desktop-bonus-car.png`.

## Pass 12 — Hardware Pixel-Art Attack FX & Limb Extension Bank
- **Problem**: Visual review of `final_step_22.png` and `09-desktop-bonus-car.png` showed that `draw_fighter()` drew procedural `out_rect` bars at neck/chest height on top of the hand-drawn `24×16` attack body poses.
- **Optimization**:
  - Populated free `CHUNK_TILES` slots `18..23` (`Punch Wave`, `Kick Slash`, `Overhead Starburst`, `Dhalsim Limb Segment`, `Dhalsim Extended Fist`, `Vega 3-Pronged Claw`) and `238` (`2×2` `16×16` Rising Dragon Flame Aura across `238, 239, 254, 255`).
  - Replaced all geometric attack rectangles in `draw_fighter()` with hardware pixel-art `spr()` effects aligned to crouch/low/standing attack heights.

## Pass 13 & 14 — Safe Identifier Compaction, Training Telemetry & Prop Themes
- **Optimization**:
  - Added quote-preserving internal helper aliasing inside `compact_lua_for_tic()` (shrinking `CHUNK_CODE` further below `65,535B`), and expanded `.tic` binary export chunks to include all 10 music patterns and all 5 tracks (`Track 4` Car Bonus BGM).
  - Added Training Mode right-side telemetry badge (`R:GRD-IDLE/AUTO/LOW ST:<stun>`) in `draw_fight_hud()` and stage-themed prop palette remapping (industrial steel drums vs crimson temple chests) in `draw_stage()`.
  - Bumped Service Worker cache in `public/sw.js` to `'sf2-ce-80-v4'`.

## Pass 15 — Authentic SF2' CE Opening Animation, 8-Track BGM, 12 Stage Landmarks & KO/Bonus/Victory Sequence
- **Problem**: The opening went straight to the static title screen, only 5 BGM tracks existed without distinct USA/World/Boss/Danger stage themes, stage landmarks lacked animated arcade details (Blanka Anaconda, Zangief molten ladle, E.Honda Rising Sun & steam, etc.), and round transitions skipped `"FIGHT!"`, KO echo screams, and score bonus tallies.
- **Optimization**:
  - Expanded `build_music()` to `24` tracker patterns and `8` full TIC-80 chiptune tracks (Opening/Select, Ryu Japan Heroic Theme, Guile/Ken/Balrog USA Syncopated Groove, Chun-Li/Blanka/Dhalsim World Warrior Theme, 4 Kings & USSR Boss Harmonic-Minor Theme, Low-HP Pinch/Danger Tempo Boost, Car Bonus/VS Funk Theme, and Stage Clear Victory Fanfare) mapped via `STG_TRK`.
  - Recreated the 3-phase *SF2' CE* Arcade Opening Animation inside `draw_title()`/`update_title()` (street crowd brawl punch & knockback -> skyscraper vertical camera pan -> rooftop lightning flash & beveled `STREET FIGHTER II'` logo slam, while skipping smoothly on button press).
  - Upgraded all 12 `draw_stage()` backdrops with authentic animated landmarks (Ryu Furinkazan board & sakura petals, Ken flapping seagulls & cargo crane, Chun-Li swaying lanterns, Guile radar & chain-link fence, Blanka coiled Anaconda with flickering tongue, E.Honda Rising Sun mural/noren/steam, Zangief pouring molten steel ladle, Dhalsim swaying elephant trunks, Balrog neon bulbs & Cadillac cruiser, Vega steel cage perimeter & petals, Sagat Buddha face/lotus plinth, M.Bison golden Temple Bell & twin Nagas).
  - Added `ROUND X` -> `FIGHT!` pre-round audio/visual callout, `round_over_t` + `ko_echo_t` KO echo screams & slow-mo knockdown, winner pose (`FS_WIN`), round-end `TIME` + `VITAL` bonus score tally UI, bruised `LOSER` portrait alongside winner flag on `draw_win()`, and expanded identifier compression aliases inside `compact_lua_for_tic()`.
- **Verification**: All 12 stages, opening intro phases, KO -> `round_over_t` progression, and `CHUNK_CODE < 65535B` pass in `verify_e2e.js`; `10-desktop-intro.png`, `01-desktop-title.png`, `02-desktop-fight.png`, and `09-desktop-bonus-car.png` visually inspected.
