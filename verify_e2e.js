#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const ticPath = resolve(root, 'sf2_ce_80.tic');
const luaPath = resolve(root, 'sf2_ce_80.lua');

function assert(cond, msg) {
  if (!cond) throw new Error(`Assertion failed: ${msg}`);
}

// 1. Validate binary .tic chunks
const ticBytes = readFileSync(ticPath);
const chunks = {};
let off = 0;
while (off + 4 <= ticBytes.length) {
  const ctype = ticBytes[off];
  const size = ticBytes.readUInt16LE(off + 1);
  const bank = ticBytes[off + 3];
  off += 4;
  chunks[ctype] = chunks[ctype] || [];
  chunks[ctype].push({ size, bank, data: ticBytes.subarray(off, off + size) });
  off += size;
}
assert(off === ticBytes.length, `.tic byte length mismatch (${off} != ${ticBytes.length})`);
assert(chunks[5] && chunks[5].length === 1, 'Missing CHUNK_CODE (5)');
assert(chunks[5][0].size < 65535, `CHUNK_CODE (${chunks[5][0].size}B) exceeds 65535B limit`);
assert(chunks[12] && chunks[12][0].size === 48, 'CHUNK_PALETTE (12) must be 48 bytes');
assert(chunks[1] && chunks[1][0].size > 0, 'Missing CHUNK_TILES (1)');
assert(chunks[9] && chunks[9][0].size > 0, 'Missing CHUNK_SAMPLES (9)');
assert(chunks[14] && chunks[14][0].size >= 8 * 51, 'Missing or truncated CHUNK_MUSIC_TRACKS (14)');
assert(chunks[15] && chunks[15][0].size >= 48 * 192, 'Missing or truncated CHUNK_MUSIC_PATTERNS (15)');

// Verify 1-based TIC-80 pattern references across all 8 tracks (0=muted, 1..48=active pattern)
const trackData = chunks[14][0].data;
const patternData = chunks[15][0].data;
for (let tr = 0; tr < 8; tr++) {
  const base = tr * 51;
  const f0 = trackData[base] | (trackData[base + 1] << 8) | (trackData[base + 2] << 16);
  const chans = [f0 & 0x3F, (f0 >> 6) & 0x3F, (f0 >> 12) & 0x3F, (f0 >> 18) & 0x3F];
  for (let ch = 0; ch < 4; ch++) {
    const patCode = chans[ch];
    assert(patCode >= 1 && patCode <= 48, `Track ${tr} frame 0 ch ${ch} has invalid 1-based pattern code ${patCode}`);
    const patSlice = patternData.subarray((patCode - 1) * 192, patCode * 192);
    assert(patSlice.some((b) => b !== 0), `Track ${tr} frame 0 ch ${ch} references empty pattern ${patCode - 1}`);
  }
}
const ticCode = chunks[5][0].data.toString('utf8');
execFileSync('luajit', ['-'], { input: `${ticCode}\nassert(type(TIC)=="function" and type(BOOT)=="function")\n`, cwd: root, encoding: 'utf8' });
console.log(`[e2e] .tic binary verified: code=${chunks[5][0].size}B (<65535B, luajit syntax OK), palette=48B, chunks=${Object.keys(chunks).length}`);

// 2. Execute LuaJIT headless simulation across all 12 fighters & authentic SF2 mechanics
const luaSource = readFileSync(luaPath, 'utf8');
const injectedHarness = `
local _btn = {}
local _prev_btn = {}
local _key = {}
local _prev_key = {}
local _prints = {}
local _pmem_writes = 0
local _cur_screen = "INIT"
local _orig_print = print

function cls() end
function pix() end
function rect() end
function rectb() end
function circ() end
function circb() end
function elli() end
function ellib() end
function line() end
function tri() end
function spr() end
function poke() end
function poke4() end
function peek() return 0 end
function peek4() return 0 end
function sfx() end
function music() end
function time() return 0 end
function pmem(idx, val)
  if val ~= nil then _pmem_writes = _pmem_writes + 1 end
  return 0
end
function btn(id) return _btn[id] == true end
function btnp(id) return _btn[id] == true and _prev_btn[id] ~= true end
function key(id) return _key[id] == true end
function keyp(id) return _key[id] == true and _prev_key[id] ~= true end
function print(txt, x, y, col, fixed, scale, small)
  table.insert(_prints, { screen=_cur_screen, txt=tostring(txt), x=x or 0, y=y or 0, scale=scale or 1, small=small==true })
end

${luaSource}

local function assert_t(cond, msg)
  if not cond then error("LUA_ASSERT_FAIL: " .. msg) end
end

local function step_frame(bmap, kmap)
  for i=0,15 do _prev_btn[i] = _btn[i]; _btn[i] = (bmap and bmap[i]) or false end
  for i=0,64 do _prev_key[i] = _key[i]; _key[i] = (kmap and kmap[i]) or false end
  TIC()
end

-- Check 12 fighters exist and SP_TBL has 3 specials each
assert_t(#CHARS == 12, "Expected 12 fighters, got " .. #CHARS)
for i=1,12 do
  assert_t(SP_TBL[i] and #SP_TBL[i] == 3, "Fighter " .. i .. " missing 3 specials")
end

-- Helper to set facing-relative buttons for P1 (facing=1 by default)
local function set_rel(rel, btns)
  local m = {}
  if rel == 8 or rel == 7 or rel == 9 then m[0] = true end
  if rel == 2 or rel == 1 or rel == 3 then m[1] = true end
  if rel == 4 or rel == 7 or rel == 1 then m[2] = true end
  if rel == 6 or rel == 9 or rel == 3 then m[3] = true end
  if btns then for _, b in ipairs(btns) do m[b] = true end end
  return m
end

-- Test all 12 fighters: normals + throws + all 36 special inputs execute and inflict damage/spawn projectile
for cid=1,12 do
  state = ST_FIGHT; game_mode = 2; paused = false; turbo = false
  start_match(cid, (cid % 12) + 1, 2)
  freeze_t = 0; match_banner_t = 0
  P1.x = 120; P2.x = 160; P1.facing = 1; P2.facing = -1

  -- Test normal LP connects
  P1.x = 132; P2.x = 148
  step_frame(set_rel(5, {4})) -- Z = LP
  for _=1,10 do step_frame({}) end
  assert_t(P2.hp < CHARS[(cid % 12) + 1].hp, CHARS[cid].name .. " normal LP failed to deal damage")

  -- Test all 3 specials for fighter cid
  for sp=1,3 do
    start_match(cid, (cid % 12) + 1, 2); freeze_t = 0; match_banner_t = 0
    P1.x = 120; P2.x = 152; P1.facing = 1; P2.facing = -1
    if cid==1 or cid==2 then
      if sp==1 then step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {4}))
      elseif sp==2 then step_frame(set_rel(6)); step_frame(set_rel(2)); step_frame(set_rel(3, {6}))
      else step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {5})) end
    elseif cid==3 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then step_frame(set_rel(5,{5})); step_frame({}); step_frame(set_rel(5,{5})); step_frame({}); step_frame(set_rel(5,{5})); step_frame({}); step_frame(set_rel(5,{5}))
      else for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5})) end
    elseif cid==4 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5}))
      else step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {4})) end
    elseif cid==5 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4}))
      else for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5})) end
    elseif cid==6 then
      if sp==1 then step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4})); step_frame({}); step_frame(set_rel(5,{4}))
      elseif sp==2 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      else for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5})) end
    elseif cid==7 then
      if sp==1 then P1.x=136; P2.x=152; step_frame(set_rel(2)); step_frame(set_rel(6)); step_frame(set_rel(8)); step_frame(set_rel(4, {4}))
      elseif sp==2 then step_frame(set_rel(5, {6, 7}))
      else step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {5})) end
    elseif cid==8 then
      if sp==1 then step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {4}))
      elseif sp==2 then step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {4}))
      else step_frame(set_rel(6)); step_frame(set_rel(2)); step_frame(set_rel(3, {5})) end
    elseif cid==9 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {5}))
      else for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {4})) end
    elseif cid==10 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5}))
      else step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {5})) end
    elseif cid==11 then
      if sp==1 then step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {4}))
      elseif sp==2 then step_frame(set_rel(6)); step_frame(set_rel(2)); step_frame(set_rel(3, {6}))
      else step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {5})) end
    elseif cid==12 then
      if sp==1 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {4}))
      elseif sp==2 then for _=1,34 do step_frame(set_rel(4)) end; step_frame(set_rel(6, {5}))
      else for _=1,34 do step_frame(set_rel(2)) end; step_frame(set_rel(8, {5})) end
    end
    assert_t(P1.st == FS_ATTACK and P1.atk and P1.atk.sp == sp, CHARS[cid].name .. " failed to trigger sp=" .. sp)
    for _=1,50 do step_frame({}) end
    if cid==8 and sp==3 then
      assert_t(P1.x ~= 120, "Dhalsim Teleport did not reposition")
    elseif sp==1 and SP_TBL[cid][1].fire==1 then
      assert_t(P2.hp < CHARS[(cid % 12) + 1].hp, CHARS[cid].name .. " projectile failed to hit P2")
    else
      assert_t(P2.hp < CHARS[(cid % 12) + 1].hp, CHARS[cid].name .. " special #" .. sp .. " failed to damage P2")
    end
  end
end

-- Test Normal -> Special Cancel 2-hit Combo + Hitstop
state = ST_FIGHT; game_mode = 2; paused = false; turbo = false
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 132; P2.x = 152; P1.facing = 1; P2.facing = -1
step_frame(set_rel(5, {6})) -- Ryu cr/st HP
for _=1,7 do step_frame({}) end
assert_t(hitstop > 0, "Hitstop failed to activate on HP connect")
-- Cancel during hitstop into 623 Shoryuken
step_frame(set_rel(6)); step_frame(set_rel(2)); step_frame(set_rel(3, {6}))
for _=1,25 do step_frame({}) end
assert_t(P1.combo_cnt >= 2, "Normal->Special cancel did not build >=2 hit combo (got " .. P1.combo_cnt .. ")")

-- Test High/Low Guard + Chip Damage + Overhead
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 128; P2.x = 150; P1.facing = 1; P2.facing = -1
local p2_start_hp = P2.hp
-- P2 holds crouch block (raw[2]=Down + raw[4]=Right relative to facing -1)
step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {4, 11})) -- P1 236+P Hadouken vs P2 blocking
for _=1,20 do step_frame({[11]=true}) end -- hold Right (btn 11=P2 right)
local blocked_proj_ok = (P2.hp < p2_start_hp and P2.hp >= p2_start_hp - 4)
assert_t(blocked_proj_ok, "Blocked Hadouken should deal chip damage (~3) instead of full 10 (hp=" .. P2.hp .. "/" .. p2_start_hp .. ")")

-- Test standing vs crouch guard against Guile Overhead (Spin Backfist)
start_match(4, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 130; P2.x = 148; P1.facing = 1; P2.facing = -1
step_frame(set_rel(2)); step_frame(set_rel(1)); step_frame(set_rel(4, {4, 9, 11})) -- P2 holds down+back (btn 9=Down, 11=Right)
for _=1,16 do step_frame({[9]=true, [11]=true}) end
assert_t(P2.hp < CHARS[2].hp - 4, "Overhead should break crouching guard (hp=" .. P2.hp .. ")")

-- Test LP slow vs HP fast fireball speeds + Ryu Forward+LP Collarbone Overhead
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 80; P2.x = 240; P1.facing = 1; P2.facing = -1
step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {4})) -- LP Hadouken
for _=1,12 do step_frame({}) end
assert_t(#projs >= 1, "LP Hadouken failed to spawn")
local lp_vx = math.abs(projs[1].vx)
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 80; P2.x = 240; P1.facing = 1; P2.facing = -1
step_frame(set_rel(2)); step_frame(set_rel(3)); step_frame(set_rel(6, {6})) -- HP Hadouken
for _=1,12 do step_frame({}) end
assert_t(#projs >= 1 and math.abs(projs[1].vx) > lp_vx + 0.5, string.format("HP fireball must be faster than LP (lp=%.2f, hp=%.2f)", lp_vx, projs[1] and math.abs(projs[1].vx) or 0))
-- Ryu Forward+LP Overhead breaks crouching block
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 132; P2.x = 148; P1.facing = 1; P2.facing = -1
step_frame(set_rel(6, {4, 9, 11}))
for _=1,16 do step_frame({[9]=true, [11]=true}) end
assert_t(P2.hp < CHARS[2].hp - 4, "Ryu 6+LP Collarbone Overhead failed to break crouch block (hp=" .. P2.hp .. ")")

-- Test Close Throw bypasses Standing Guard
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P1.x = 132; P2.x = 148; P1.facing = 1; P2.facing = -1
step_frame(set_rel(6, {6, 11})) -- P1 6+HP vs P2 holding back
for _=1,5 do step_frame({}) end
assert_t(P1.st == FS_THROW and P2.st == FS_KD, "Close Throw failed against guarding opponent")

-- Test Corner Pushback Transfer
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P2.x = STG_W - 16; P1.x = STG_W - 34; P1.facing = 1; P2.facing = -1
local pre_p1x = P1.x
step_frame(set_rel(5, {6})) -- HP hit against cornered P2
for _=1,12 do step_frame({}) end
assert_t(P1.x < pre_p1x - 4, "Corner pushback transfer failed to push P1 backward (" .. P1.x .. " vs " .. pre_p1x .. ")")

-- Test Dizzy & Mash Recovery
start_match(1, 2, 2); freeze_t = 0; match_banner_t = 0
P2.stun = 95; P1.x = 130; P2.x = 150
step_frame(set_rel(5, {6}))
for _=1,16 do step_frame({}) end
assert_t(P2.st == FS_DIZZY, "High stun failed to trigger FS_DIZZY (st=" .. P2.st .. ", stun=" .. P2.stun .. ")")
local dt1 = P2.dizzy_t
step_frame({[12]=true}) -- mash P2 button
assert_t(P2.dizzy_t <= dt1 - 5, "Dizzy mash recovery did not accelerate wakeup")

-- Test Car Bonus Stage destruction
start_car_bonus()
assert_t(state == ST_BONUS and car.hp == 100, "Car bonus failed to initialize")
for _=1,60 do
  P1.x = 134
  step_frame({[6]=true}) -- mash HP
  step_frame({})
end
assert_t(car.hp < 100, "Car Bonus did not take damage")
for _=1,300 do
  if car.hp <= 0 then break end
  P1.x = 134; step_frame({[6]=true}); step_frame({})
end
assert_t(car.done and car.hp == 0 and p1_score >= 30000, "Car Bonus did not complete with +30000 PERFECT bonus")

-- Test CE vs Hyper Fighting (Turbo) frame cadence
turbo = false; state = ST_FIGHT; start_match(1, 2, 2); freeze_t = 0; P1.x = 120
for _=1,4 do step_frame({[3]=true}) end
local ce_x = P1.x
turbo = true; state = ST_FIGHT; start_match(1, 2, 2); freeze_t = 0; P1.x = 120
for _=1,4 do step_frame({[3]=true}) end
local hf_x = P1.x
assert_t(hf_x > ce_x, "Hyper Fighting turbo did not advance faster than Champion speed (" .. hf_x .. " <= " .. ce_x .. ")")

-- Test 480f Title Attract Mode & No PMEM writes & exits cleanly on input
state = ST_TITLE; title_idle = 0; is_attract = false; turbo = false
_pmem_writes = 0
for _=1,482 do step_frame({}) end
assert_t(state == ST_ATTRACT and is_attract == true, "Title did not enter Attract Mode after 480f idle (state=" .. state .. ")")
step_frame({})
step_frame({[4]=true})
assert_t(state == ST_TITLE and is_attract == false, "Attract Mode did not exit to Title on input")
assert_t(_pmem_writes == 0, "Title/Attract wrote to pmem unexpectedly")

-- Test Round-End KO sequence, Bonus Tally, 12 Stage Backgrounds & 3-Phase Opening Animation
start_match(1, 2, 1); state = ST_FIGHT; game_mode = 1; freeze_t = 0; match_banner_t = 0
P1.wins = 0; P2.wins = 0; P2.hp = 0; p1_score = 0
step_frame({})
assert_t(round_over_t > 0 and P1.wins == 1, "KO did not enter round_over_t and award P1 win")
assert_t(match_banner == "K.O.!" or match_banner == "PERFECT!", "Unexpected KO banner: " .. match_banner)
assert_t(p1_score >= 2000, "KO bonus score not awarded")
for _=1,95 do step_frame({}) end
assert_t(round_over_t == 0 and round_num == 2 and state == ST_FIGHT, "Round did not advance cleanly after round_over_t (rt=" .. round_over_t .. ", rn=" .. round_num .. ")")

-- Test 240x136 print() bounds across EVERY screen, intro phase, stage, KO bonus & guide page
_prints = {}
for _, tid in ipairs({10, 60, 95, 130}) do
  _cur_screen = "INTRO_" .. tid; state = ST_TITLE; title_idle = tid; draw_title()
end
for sid=1,12 do
  _cur_screen = "STAGE_" .. sid; cur_stage = sid; draw_stage(sid, 40)
end
_cur_screen = "TITLE"; state = ST_TITLE; title_idle = 130; step_frame({})
_cur_screen = "SELECT"; state = ST_SELECT; step_frame({})
_cur_screen = "VS"; state = ST_VS; freeze_t = 10; step_frame({})
_cur_screen = "FIGHT_TRN"; state = ST_FIGHT; game_mode = 3; show_hitboxes = true; start_match(1, 12, 3); step_frame({})
_cur_screen = "ROUND_OVER_UI"; state = ST_FIGHT; game_mode = 1; P2.hp = 0; round_over_t = 40; match_banner = "K.O.!"; match_banner_t = 40; step_frame({})
round_over_t = 0
_cur_screen = "BONUS"; start_car_bonus(); step_frame({})
_cur_screen = "WIN"; state = ST_WIN; P1.wins = 2; P2.wins = 0; freeze_t = 40; step_frame({})
for gp=1,4 do
  _cur_screen = "GUIDE_" .. gp; state = ST_GUIDE; guide_page = gp; step_frame({})
end

for _, pr in ipairs(_prints) do
  local char_w = pr.small and 4 or (6 * pr.scale)
  local rw = #pr.txt * char_w
  assert_t(pr.x >= 0 and pr.x + rw <= 246, string.format("Print out of X bounds [%s]: '%s' x=%d w=%d", pr.screen, pr.txt, pr.x, rw))
  assert_t(pr.y >= 0 and pr.y <= 132, string.format("Print out of Y bounds [%s]: '%s' y=%d", pr.screen, pr.txt, pr.y))
end
_orig_print("[lua-e2e] ALL 12 FIGHTERS, 36 SPECIALS, SF2 MECHANICS, BONUS, ATTRACT, BOUNDS PASSED (" .. #_prints .. " prints checked)")
`;

const out = execFileSync('luajit', ['-'], { input: injectedHarness, cwd: root, encoding: 'utf8' });
process.stdout.write(out);
console.log('[e2e] Complete PASS.');
