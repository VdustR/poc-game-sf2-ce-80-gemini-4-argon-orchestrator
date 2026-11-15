-- title:  SF2' CHAMPION EDITION 80
-- author: SF2' CE NGPC Tribute
-- desc:   Street Fighter II': Champion Edition (NGPC Chibi Style)
-- version: 1.0.0
-- script: lua

local floor, abs, min, max, sin, cos = math.floor, math.abs, math.min, math.max, math.sin, math.cos
local rand = math.random

local ST_TITLE, ST_SELECT, ST_VS, ST_FIGHT, ST_BONUS, ST_WIN, ST_GUIDE, ST_ATTRACT = 0, 1, 2, 3, 4, 5, 6, 7
local FS_IDLE, FS_WALKF, FS_WALKB, FS_CROUCH, FS_PREJUMP, FS_JUMP = 0, 1, 2, 3, 4, 5
local FS_ATTACK, FS_BLOCK_S, FS_BLOCK_C, FS_HIT, FS_KD, FS_WAKE = 6, 7, 8, 9, 10, 11
local FS_DIZZY, FS_WIN, FS_LOSE, FS_THROW = 12, 13, 14, 15
local STG_W, FLOOR_Y, GRAV = 320, 120, 0.24

local CHARS = {
  { id=1, name="RYU", country="JAPAN", stage="SUZAKU CASTLE", quote="YOU MUST DEFEAT SHENG LONG TO STAND A CHANCE!",
    spd_f=1.35, spd_b=1.15, jvy=-4.25, jvx=1.95, hp=100, p1={4,5,1,2,7,6,14}, p2={4,5,13,12,9,0,14},
    sp={"HADOUKEN","SHORYUKEN","TATSUMAKI"}, cmd={"236+P","623+P","214+K"} },
  { id=2, name="KEN", country="U.S.A.", stage="HARBOR DOCK", quote="ATTACK ME IF YOU DARE, I WILL CRUSH YOU!",
    spd_f=1.45, spd_b=1.22, jvy=-4.30, jvx=2.05, hp=100, p1={4,5,7,6,9,9,8}, p2={4,5,12,13,1,9,14},
    sp={"HADOUKEN","FLAME DP","TATSUMAKI"}, cmd={"236+P","623+P","214+K"} },
  { id=3, name="CHUN-LI", country="CHINA", stage="TAIPING MARKET", quote="THERE IS NO CHANCE FOR YOU TO BEAT MY KICK!",
    spd_f=1.72, spd_b=1.50, jvy=-4.45, jvx=2.25, hp=96, p1={4,5,12,13,9,6,14}, p2={4,5,7,6,9,6,9},
    sp={"KIKOKEN","LIGHTNING KICK","SPIN BIRD"}, cmd={"[4]6+P","MASH K","[2]8+K"} },
  { id=4, name="GUILE", country="U.S.A.", stage="AIR FORCE BASE", quote="GO HOME AND BE A FAMILY MAN!",
    spd_f=1.28, spd_b=1.14, jvy=-4.20, jvx=1.88, hp=102, p1={4,5,10,11,3,9,14}, p2={4,5,12,13,3,9,9},
    sp={"SONIC BOOM","FLASH KICK","SPIN BACKFIST"}, cmd={"[4]6+P","[2]8+K","214+P"} },
  { id=5, name="BLANKA", country="BRAZIL", stage="AMAZON RIVER", quote="SEEING YOU IN ACTION IS A JOKE!",
    spd_f=1.38, spd_b=1.20, jvy=-4.30, jvx=2.10, hp=104, p1={10,11,6,5,9,8,14}, p2={5,6,13,12,8,7,14},
    sp={"ROLL ATTACK","ELEC THUNDER","VERT ROLL"}, cmd={"[4]6+P","MASH P","[2]8+K"} },
  { id=6, name="E.HONDA", country="JAPAN", stage="SENTOU BATHHOUSE", quote="CAN'T YOU DO BETTER THAN THAT? SUMO RULES!",
    spd_f=1.05, spd_b=0.92, jvy=-4.05, jvx=1.65, hp=110, p1={4,5,12,13,7,0,14}, p2={5,6,15,13,8,0,9},
    sp={"100 HAND SLAP","SUMO HEADBUTT","SUMO SMASH"}, cmd={"MASH P","[4]6+P","[2]8+K"} },
  { id=7, name="ZANGIEF", country="U.S.S.R.", stage="STEEL FOUNDRY", quote="MY IRON BODY IS INVINCIBLE!",
    spd_f=0.92, spd_b=0.80, jvy=-3.95, jvx=1.50, hp=118, p1={5,6,7,6,9,6,8}, p2={5,6,12,13,9,6,14},
    sp={"SCREW PILEDRV","DOUBLE LARIAT","SIBERIAN SLAM"}, cmd={"360+P","236+P/2P","214+K"} },
  { id=8, name="DHALSIM", country="INDIA", stage="ELEPHANT TEMPLE", quote="I WILL MEDITATE AND THEN DESTROY YOU!",
    spd_f=0.88, spd_b=0.76, jvy=-3.90, jvx=1.55, hp=96, p1={5,6,9,8,7,1,8}, p2={3,13,8,7,1,14,8},
    sp={"YOGA FIRE","YOGA FLAME","YOGA TELEPORT"}, cmd={"236+P","214+P","623+K"} },
  { id=9, name="BALROG", country="U.S.A.", stage="LAS VEGAS STRIP", quote="MY FISTS HAVE YOUR BLOOD ON THEM!",
    spd_f=1.42, spd_b=1.22, jvy=-4.15, jvx=1.90, hp=108, p1={6,5,12,13,7,0,8}, p2={5,6,7,6,12,0,9},
    sp={"DASH STRAIGHT","DASH UPPER","BUFFALO HEAD"}, cmd={"[4]6+P","[4]6+K","[2]8+P"} },
  { id=10, name="VEGA", country="SPAIN", stage="FLAMENCO TAVERN", quote="HANDSOME FIGHTERS NEVER LOSE BATTLES!",
    spd_f=1.70, spd_b=1.55, jvy=-4.55, jvx=2.35, hp=98, p1={4,5,15,13,9,6,2}, p2={4,5,7,6,1,6,2},
    sp={"CRYSTAL FLASH","SKY HIGH CLAW","SCARLET TERROR"}, cmd={"[4]6+P","[2]8+K","214+K"} },
  { id=11, name="SAGAT", country="THAILAND", stage="BUDDHA RUINS", quote="YOU ARE NOT A WARRIOR, YOU ARE A BEGINNER!",
    spd_f=1.18, spd_b=1.02, jvy=-4.15, jvx=1.80, hp=110, p1={5,6,12,13,7,1,9}, p2={5,6,10,11,9,1,9},
    sp={"TIGER SHOT","TIGER UPPER","TIGER KNEE"}, cmd={"236+P/K","623+P","214+K"} },
  { id=12, name="M.BISON", country="THAILAND", stage="SHADALOO TEMPLE", quote="ANYONE WHO OPPOSES ME WILL BE DESTROYED!",
    spd_f=1.50, spd_b=1.30, jvy=-4.30, jvx=2.12, hp=112, p1={5,6,7,6,9,0,15}, p2={5,6,13,12,9,0,14},
    sp={"PSYCHO CRUSH","SCISSOR KICK","HEAD STOMP"}, cmd={"[4]6+P","[4]6+K","[2]8+K"} },
}

-- Data-driven 36 Special Move Table: {name, sfx, dmg, chip, stun, su, act, rec, reach, hy, hh, vx, vy, inv, pinv, kd, over, grab, multi, fire, kind, spd}
local SP_TBL = {
  [1]={
    {nm="HADOUKEN",sfx=6,su=8,act=2,rec=18,fire=1,kind="HADOU",spd=1.75,hspd=2.65,dmg=10,hd=12,hs=9},
    {nm="SHORYUKEN",sfx=7,dmg=14,hd=18,chip=3,stun=22,su=3,act=14,rec=14,reach=20,hy=-36,hh=34,kd=1,push=16,hs=11,vx=1.0,vy=-3.9,hvy=-4.5,inv=8},
    {nm="TATSUMAKI",sfx=2,dmg=12,hd=14,chip=3,stun=16,su=4,act=22,rec=9,reach=24,hy=-28,hh=22,kd=1,push=16,hs=10,vx=2.1,vy=-1.1,pinv=20},
  },
  [2]={
    {nm="HADOUKEN",sfx=6,su=8,act=2,rec=17,fire=1,kind="HADOU",spd=1.85,hspd=2.75,dmg=10,hd=12,hs=9},
    {nm="FLAME SHORYU",sfx=7,dmg=15,hd=19,chip=4,stun=22,su=3,act=14,rec=14,reach=20,hy=-36,hh=34,kd=1,push=16,hs=11,vx=1.2,vy=-4.1,hvy=-4.6,inv=8},
    {nm="TATSUMAKI",sfx=2,dmg=12,hd=15,chip=3,stun=16,su=4,act=22,rec=9,reach=24,hy=-28,hh=22,kd=1,push=16,hs=10,vx=2.5,vy=-1.1,pinv=20},
  },
  [3]={
    {nm="KIKOKEN",sfx=6,su=8,act=2,rec=16,fire=1,kind="HADOU",spd=1.70,hspd=2.50,dmg=10,hd=11,hs=9},
    {nm="LIGHTNING KICK",sfx=3,dmg=14,hd=16,chip=4,stun=16,su=4,act=20,rec=8,reach=26,hy=-28,hh=22,push=12,hs=9,multi=1},
    {nm="SPIN BIRD KICK",sfx=2,dmg=15,hd=17,chip=3,stun=18,su=5,act=22,rec=10,reach=26,hy=-28,hh=22,kd=1,push=15,hs=10,vx=2.4,vy=-1.2},
  },
  [4]={
    {nm="SONIC BOOM",sfx=6,su=7,act=2,rec=11,fire=1,kind="BOOM",spd=1.80,hspd=2.75,dmg=11,hd=12,hs=9},
    {nm="FLASH KICK",sfx=7,dmg=16,hd=18,chip=3,stun=20,su=3,act=14,rec=14,reach=26,hy=-38,hh=34,kd=1,push=18,hs=11,vx=1.0,vy=-4.3,inv=9},
    {nm="SPIN BACKFIST",sfx=4,dmg=14,hd=15,chip=2,stun=18,su=8,act=5,rec=11,reach=24,hy=-30,hh=20,over=1,push=14,hs=10,vx=1.2},
  },
  [5]={
    {nm="ROLL ATTACK",sfx=2,dmg=15,hd=17,chip=3,stun=18,su=4,act=20,rec=12,reach=20,hy=-26,hh=22,kd=1,push=16,hs=10,vx=2.8,hvx=3.6},
    {nm="ELEC THUNDER",sfx=10,dmg=14,hd=16,chip=4,stun=18,su=3,act=20,rec=8,reach=28,hy=-32,hh=28,kd=1,push=14,hs=10,multi=1},
    {nm="VERT ROLL",sfx=7,dmg=15,hd=17,chip=3,stun=18,su=4,act=18,rec=12,reach=22,hy=-34,hh=30,kd=1,push=16,hs=10,vx=1.4,vy=-4.6},
  },
  [6]={
    {nm="100 HAND SLAP",sfx=3,dmg=15,hd=17,chip=4,stun=18,su=3,act=22,rec=8,reach=28,hy=-30,hh=24,push=12,hs=9,multi=1},
    {nm="SUMO HEADBUTT",sfx=4,dmg=16,hd=18,chip=3,stun=22,su=5,act=18,rec=12,reach=22,hy=-28,hh=22,kd=1,push=18,hs=11,vx=2.7,hvx=3.5},
    {nm="SUMO SMASH",sfx=9,dmg=16,hd=18,chip=3,stun=20,su=6,act=22,rec=10,reach=22,hy=-22,hh=24,over=1,kd=1,push=14,hs=11,vx=2.0,vy=-4.2},
  },
  [7]={
    {nm="SCREW PILEDRV",sfx=9,dmg=26,hd=28,chip=0,stun=28,su=2,act=4,rec=18,reach=32,hy=-32,hh=30,grab=1,kd=1,push=22,hs=12},
    {nm="DOUBLE LARIAT",sfx=2,dmg=15,hd=16,chip=2,stun=18,su=4,act=24,rec=10,reach=26,hy=-32,hh=26,kd=1,push=16,hs=10,pinv=28},
    {nm="SIBERIAN SLAM",sfx=4,dmg=18,hd=20,chip=3,stun=22,su=7,act=14,rec=13,reach=22,hy=-30,hh=26,kd=1,push=18,hs=11,vx=2.8},
  },
  [8]={
    {nm="YOGA FIRE",sfx=6,su=9,act=2,rec=17,fire=1,kind="YOGA",spd=1.40,hspd=2.15,dmg=11,hd=12,hs=9},
    {nm="YOGA FLAME",sfx=8,dmg=16,hd=18,chip=4,stun=20,su=8,act=14,rec=14,reach=30,hy=-28,hh=22,kd=1,push=16,hs=10},
    {nm="YOGA TELEPORT",sfx=10,dmg=0,su=2,act=2,rec=12,reach=0,hy=0,hh=0,inv=16,tp=1},
  },
  [9]={
    {nm="DASH STRAIGHT",sfx=4,dmg=16,hd=18,chip=3,stun=22,su=5,act=14,rec=11,reach=26,hy=-28,hh=20,kd=1,push=16,hs=11,vx=3.0,hvx=3.8},
    {nm="DASH UPPER",sfx=7,dmg=15,hd=17,chip=3,stun=20,su=5,act=14,rec=12,reach=24,hy=-34,hh=26,kd=1,push=16,hs=11,vx=3.0,vy=-1.6},
    {nm="BUFFALO HEAD",sfx=7,dmg=17,hd=19,chip=3,stun=24,su=4,act=12,rec=14,reach=22,hy=-36,hh=28,kd=1,push=16,hs=11,vx=1.1,vy=-3.9,inv=8},
  },
  [10]={
    {nm="CRYSTAL FLASH",sfx=2,dmg=14,hd=16,chip=3,stun=16,su=4,act=18,rec=10,reach=26,hy=-28,hh=22,kd=1,push=14,hs=9,vx=3.3},
    {nm="SKY HIGH CLAW",sfx=7,dmg=15,hd=17,chip=3,stun=16,su=5,act=20,rec=10,reach=26,hy=-26,hh=24,over=1,kd=1,push=14,hs=10,vx=2.9,vy=-4.2},
    {nm="SCARLET TERROR",sfx=7,dmg=15,hd=17,chip=3,stun=18,su=4,act=14,rec=12,reach=24,hy=-34,hh=28,kd=1,push=16,hs=10,vx=1.6,vy=-3.8,inv=8},
  },
  [11]={
    {nm="TIGER SHOT",sfx=6,su=8,act=2,rec=15,fire=1,kind="TIGER",spd=1.85,hspd=2.85,dmg=11,hd=12,hs=9},
    {nm="TIGER UPPER",sfx=7,dmg=20,hd=22,chip=4,stun=24,su=3,act=14,rec=15,reach=22,hy=-38,hh=36,kd=1,push=18,hs=11,vx=1.1,vy=-4.4,inv=9},
    {nm="TIGER KNEE",sfx=4,dmg=16,hd=18,chip=3,stun=18,su=5,act=16,rec=11,reach=22,hy=-32,hh=26,kd=1,push=16,hs=10,vx=3.1,vy=-2.4},
  },
  [12]={
    {nm="PSYCHO CRUSH",sfx=6,dmg=17,hd=19,chip=4,stun=22,su=5,act=22,rec=12,reach=24,hy=-28,hh=22,kd=1,push=18,hs=11,vx=3.1,hvx=3.8,inv=6},
    {nm="SCISSOR KICK",sfx=4,dmg=15,hd=17,chip=3,stun=18,su=5,act=20,rec=9,reach=26,hy=-26,hh=22,kd=1,push=14,hs=10,vx=3.2,vy=-2.5},
    {nm="HEAD STOMP",sfx=7,dmg=16,hd=18,chip=3,stun=20,su=5,act=24,rec=12,reach=20,hy=-20,hh=22,over=1,kd=1,push=14,hs=10,vx=2.3,vy=-4.5},
  },
}

local state, prev_state, t, turbo, turbo_acc = ST_TITLE, ST_TITLE, 0, false, 0
local game_mode, title_cursor, title_idle, is_attract, attract_t = 1, 1, 0, false, 0
local paused, sfx_muted, show_hitboxes, trn_guard, guide_page = false, false, false, 1, 1
local p1_pick, p2_pick, p1_ready, p2_ready, p1_cursor, p2_cursor = 1, 2, false, false, 1, 2
local arcade_idx, arcade_order, p1_score, round_num = 1, {1,2,3,4,5,6,7,8,9,10,11,12}, 0, 1
local timer_sec, timer_sub, match_banner, match_banner_t = 99, 0, "", 0
local freeze_t, hitstop, shake_t, shake_amp, cam_x, cur_stage = 0, 0, 0, 0, 40, 1
local first_hit_done, round_over_t, ko_echo_t = false, 0, 0
local STG_TRK = {1,2,3,2,3,1,4,3,2,4,4,4}
local props, projs, fx, popups = {}, {}, {}, {}
local car = { x=176, hp=100, max_hp=100, hit_t=0, time=20, sub=0, done=false }

local inp = {{},{}}
for i=1,2 do
  inp[i] = { raw={}, prev={}, p={}, r={}, hold={}, log={} }
  for b=1,8 do inp[i].raw[b]=false; inp[i].prev[b]=false; inp[i].p[b]=false; inp[i].r[b]=false; inp[i].hold[b]=0 end
end
local prev_hold = {{0,0,0,0,0,0,0,0},{0,0,0,0,0,0,0,0}}

local function sfx_play(id, note, dur, ch, vol)
  if sfx_muted or is_attract then return end
  sfx(id, note or -1, dur or -1, ch or 0, vol or 12)
end

local cur_track = -1
local function sync_music(tr)
  if sfx_muted or is_attract or paused then
    if cur_track ~= -1 then music(-1); cur_track = -1 end
    return
  end
  if tr ~= nil and tr ~= cur_track then music(tr); cur_track = tr end
end

local function pal_reset() for i=0,15 do poke4(0x3FF0*2+i, i) end end
local function pal_remap(src, dst) poke4(0x3FF0*2+src, dst) end
local function set_char_pal(p, flash)
  pal_remap(15, 0)
  if flash then
    pal_remap(2, 1); pal_remap(3, 1); pal_remap(4, 1); pal_remap(5, 1)
    pal_remap(6, 1); pal_remap(7, 14); pal_remap(14, 1)
  else
    pal_remap(4, p[1]); pal_remap(5, p[2]); pal_remap(2, p[3]); pal_remap(3, p[4])
    pal_remap(7, p[5]); pal_remap(6, p[6]); pal_remap(14, p[7])
  end
end
local function dither_seam(y, col)
  pal_remap(1, col)
  for rx=0,29 do spr(13, rx*8, y, 0) end
  pal_reset()
end
local function out_rect(x, y, w, h, c) rect(x-1, y-1, w+2, h+2, 0); rect(x, y, w, h, c) end
local function out_circ(x, y, r, c) circ(x, y, r+1, 0); circ(x, y, r, c) end

local function make_fighter(slot, char_id, is_cpu, is_2p_col)
  local c = CHARS[char_id]
  local db = {}
  for i=1,20 do db[i] = 5 end
  return {
    slot=slot, cid=char_id, c=c, is_cpu=is_cpu,
    pal = is_2p_col and c.p2 or c.p1,
    x = slot==1 and 112 or 208, y = FLOOR_Y, vx=0, vy=0,
    facing = slot==1 and 1 or -1,
    hp=c.hp, max_hp=c.hp, red_hp=c.hp,
    stun=0, stun_decay=0, dizzy_t=0, wins=0, st=FS_IDLE, st_t=0, pj_dir=0,
    atk=nil, combo_cnt=0, combo_show_t=0,
    invuln_t=0, throw_invuln=0, proj_invuln=0, hitstun_t=0, blockstun_t=0, wake_t=0,
    dir_buf=db, chg_b=0, chg_b_keep=0, chg_d=0, chg_d_keep=0, mash_p={}, mash_k={},
    buf_btn=0, buf_btn_t=0, cpu_t=0
  }
end

local P1, P2

local function read_all_inputs()
  local k = key or function() return false end
  local r1 = {
    btn(0), btn(1), btn(2), btn(3),
    btn(4) or (k(21) and game_mode ~= 2),
    btn(5) or (k(10) and game_mode ~= 2),
    btn(6), btn(7)
  }
  local r2 = {
    btn(8)  or k(9),
    btn(9)  or k(11),
    btn(10) or k(10),
    btn(11) or k(12),
    btn(12) or k(25) or k(45),
    btn(13) or k(14) or k(46),
    btn(14) or k(21) or k(15),
    btn(15) or k(8)  or k(47),
  }
  local arr = {r1, r2}
  for s=1,2 do
    local d = inp[s]
    for b=1,8 do
      d.prev[b] = d.raw[b]
      d.raw[b] = arr[s][b] or false
      d.p[b] = d.raw[b] and not d.prev[b]
      d.r[b] = not d.raw[b] and d.prev[b]
      d.hold[b] = d.raw[b] and (d.hold[b] + 1) or 0
    end
  end
end

local function any_p1_press()
  for b=1,8 do if inp[1].p[b] then return true end end
  return (keyp and (keyp(48) or keyp(50))) or false
end

local function human_any_btn()
  for s=1,2 do for b=1,8 do if inp[s].p[b] then return true end end end
  return false
end

local function get_rel_dir(slot, facing)
  local r = inp[slot].raw
  local dx = (r[4] and 1 or 0) - (r[3] and 1 or 0)
  local dy = (r[2] and 1 or 0) - (r[1] and 1 or 0)
  local fx = dx * facing
  if dy == 1 then return fx==1 and 3 or (fx==-1 and 1 or 2)
  elseif dy == -1 then return fx==1 and 9 or (fx==-1 and 7 or 8)
  else return fx==1 and 6 or (fx==-1 and 4 or 5) end
end

local DIR_GLYPHS = {"1","2","3","4","5","6","7","8","9"}
local function push_input_hist(f)
  local dir = get_rel_dir(f.slot, f.facing)
  for i=20,2,-1 do f.dir_buf[i] = f.dir_buf[i-1] end
  f.dir_buf[1] = dir
  if dir==1 or dir==4 or dir==7 then
    f.chg_b = min(90, f.chg_b + 1)
    if f.chg_b >= 32 then f.chg_b_keep = 14 end
  else
    f.chg_b = 0
    if f.chg_b_keep > 0 then f.chg_b_keep = f.chg_b_keep - 1 end
  end
  if dir==1 or dir==2 or dir==3 then
    f.chg_d = min(90, f.chg_d + 1)
    if f.chg_d >= 32 then f.chg_d_keep = 14 end
  else
    f.chg_d = 0
    if f.chg_d_keep > 0 then f.chg_d_keep = f.chg_d_keep - 1 end
  end
  local d = inp[f.slot]
  if d.p[5] or d.p[7] then table.insert(f.mash_p, t) end
  if d.p[6] or d.p[8] then table.insert(f.mash_k, t) end
  while #f.mash_p > 0 and t - f.mash_p[1] > 34 do table.remove(f.mash_p, 1) end
  while #f.mash_k > 0 and t - f.mash_k[1] > 34 do table.remove(f.mash_k, 1) end
  local atk_str = d.p[5] and "LP" or (d.p[6] and "LK" or (d.p[7] and "HP" or (d.p[8] and "HK" or "")))
  local log = inp[f.slot].log
  if (#log == 0) or dir ~= log[1].dir or atk_str ~= "" then
    if dir ~= 5 or atk_str ~= "" then
      table.insert(log, 1, {dir=dir, atk=atk_str})
      if #log > 10 then table.remove(log) end
    end
  end
end

local function match_seq(buf, seq, max_win)
  local pos = #seq
  for i=1, min(20, max_win or 15) do
    local target = seq[pos]
    local v, ok = buf[i], false
    if type(target) == "table" then
      for _, tv in ipairs(target) do if v == tv then ok = true break end end
    else ok = (v == target) end
    if ok then pos = pos - 1; if pos == 0 then return true end end
  end
  return false
end

local function has_360(buf)
  local u, d, l, r = false, false, false, false
  for i=1,20 do
    local v = buf[i]
    if v>=7 then u=true end
    if v<=3 then d=true end
    if v==1 or v==4 or v==7 then l=true end
    if v==3 or v==6 or v==9 then r=true end
  end
  return u and d and l and r
end

local function get_atk_trigger(f, allow_neg)
  local d = inp[f.slot]
  for b=5,8 do if d.p[b] then return b-4, false end end
  if allow_neg then
    for b=5,8 do
      if d.r[b] and prev_hold[f.slot][b] >= 3 and prev_hold[f.slot][b] <= 45 then
        return b-4, true
      end
    end
  end
  return 0, false
end

local function spawn_fx(kind, x, y, col, life)
  table.insert(fx, {kind=kind, x=x, y=y, col=col or 14, life=life or 12, max=life or 12})
end
local function spawn_popup(text, x, y, col)
  table.insert(popups, {text=text, x=x, y=y, col=col or 9, life=36})
end
local function add_shake(amp, dur) shake_amp=max(shake_amp, amp); shake_t=max(shake_t, dur) end

local function make_normal(f, btn_idx, is_crouch, is_air, dir)
  local reach_b = (f.cid==8) and 22 or ((f.cid==10 or f.cid==11) and 6 or 0)
  local fast = (f.cid==3 or f.cid==10 or f.cid==2)
  local hdmg = (f.cid==7 or f.cid==11 or f.cid==9) and 14 or 12
  local is_k, is_h = (btn_idx==2 or btn_idx==4), (btn_idx>=3)
  if is_air then
    if f.cid==3 and btn_idx==2 and inp[f.slot].raw[2] then
      return { name="HEAD STOMP", dmg=8, chip=0, stun=10, startup=3, active=14, rec=6,
        reach=18, hy=-6, hh=16, over=true, push=8, hitstop=8, stomp=true }
    end
    return { name=(is_h and (is_k and "J.HK" or "J.HP") or (is_k and "J.LK" or "J.LP")),
      dmg=is_h and 11 or 7, chip=0, stun=is_h and 14 or 8, startup=is_h and 5 or 3, active=is_h and 12 or 10, rec=8,
      reach=(is_k and 20 or 18)+(f.cid==8 and 14 or 0), hy=-8, hh=18, over=true, push=is_h and 12 or 8, hitstop=is_h and 9 or 6 }
  elseif is_crouch then
    if is_k and is_h then
      return { name="CR.HK", dmg=hdmg, chip=0, stun=16, startup=6, active=5, rec=15,
        reach=26+reach_b, hy=-10, hh=11, low=true, kd=true, push=14, hitstop=9 }
    end
    return { name=(is_h and "CR.HP" or (is_k and "CR.LK" or "CR.LP")),
      dmg=is_h and 11 or 6, chip=0, stun=is_h and 14 or 7, startup=is_h and 6 or (fast and 3 or 4), active=4, rec=is_h and 12 or 7,
      reach=(is_k and 22 or 20)+reach_b, hy=is_h and -30 or -12, hh=is_h and 22 or 12, low=is_k,
      push=is_h and 11 or 7, hitstop=is_h and 9 or 6, cancel=true }
  else
    if dir==6 and btn_idx==1 and (f.cid<=2 or f.cid==6 or f.cid==7) then
      return { name=(f.cid<=2 and "OVERHEAD" or "HEADBUTT"), dmg=9, chip=0, stun=13, startup=7, active=5, rec=10,
        reach=22, hy=-28, hh=20, over=(f.cid<=2 or f.cid==6), push=10, hitstop=8, vx=1.3, cancel=true }
    elseif dir==6 and btn_idx==2 and f.cid==4 then
      return { name="KNEE KICK", dmg=8, chip=0, stun=10, startup=4, active=6, rec=8,
        reach=23, hy=-24, hh=16, push=9, hitstop=7, vx=1.6, cancel=true }
    end
    return { name=(is_h and (is_k and "ST.HK" or "ST.HP") or (is_k and "ST.LK" or "ST.LP")),
      dmg=is_h and hdmg or 6, chip=0, stun=is_h and 15 or 7, startup=is_h and 7 or (fast and 3 or 4), active=4, rec=is_h and 12 or 7,
      reach=(is_k and 24 or 20)+reach_b, hy=-26, hh=16, push=is_h and 12 or 7, hitstop=is_h and 9 or 6, cancel=true }
  end
end

local function spawn_proj(f, kind, spd, dmg, hy, col1, col2)
  table.insert(projs, { owner=f.slot, kind=kind, x=f.x+f.facing*18, y=f.y+(hy or -20),
    vx=f.facing*spd, dmg=dmg, chip=3, stun=12, col1=col1 or 14, col2=col2 or 1, life=160 })
end

local function start_special(f, sp_idx, btn_idx)
  local heavy = (btn_idx >= 3)
  local s = SP_TBL[f.cid][sp_idx]
  if (f.wake_t or 0) > 0 then
    f.wake_t = 0
    spawn_popup("REVERSAL!", f.x, f.y-42, 9)
    if f.slot==1 then p1_score = p1_score + 400 end
  end
  sfx_play(s.sfx, 40, 14, 1)
  f.st = FS_ATTACK; f.st_t = 0; f.vx = 0
  if s.inv then f.invuln_t = s.inv end
  if s.pinv then f.proj_invuln = s.pinv end
  if s.tp then
    local back = (inp[f.slot].raw[3] and f.facing==1) or (inp[f.slot].raw[4] and f.facing==-1)
    f.x = max(20, min(STG_W-20, f.x + f.facing*(back and -70 or 70)))
  end
  local spd_x = heavy and (s.hvx or s.vx or 0) or (s.vx or 0)
  local spd_y = heavy and (s.hvy or s.vy or 0) or (s.vy or 0)
  if spd_x ~= 0 then f.vx = f.facing * spd_x end
  if spd_y ~= 0 then f.vy = spd_y end
  local is_low_tiger = (f.cid==11 and sp_idx==1 and (btn_idx==2 or btn_idx==4))
  f.atk = {
    name=s.nm, dmg=s.fire and 0 or (heavy and (s.hd or s.dmg) or s.dmg), chip=s.chip or 0, stun=s.stun or 0,
    startup=s.su, active=s.act, rec=s.rec, reach=s.reach or 0, hy=s.hy or 0, hh=s.hh or 0,
    over=s.over==1, kd=s.kd==1, grab=s.grab==1, multi=s.multi==1,
    push=s.push or 14, hitstop=s.hs or 10, sp=sp_idx,
    sp_fire=s.fire==1, sp_kind=s.kind, sp_spd=heavy and (s.hspd or s.spd) or s.spd,
    sp_dmg=heavy and (s.hd or s.dmg) or s.dmg, sp_hy=is_low_tiger and -11 or -23, hit=false
  }
end

local function check_special_cmd(f, btn_idx, is_air)
  if btn_idx == 0 then return false end
  local cid, buf, d = f.cid, f.dir_buf, inp[f.slot]
  local is_p = (btn_idx==1 or btn_idx==3)
  local is_k = (btn_idx==2 or btn_idx==4)
  if is_air then
    if (cid==1 or cid==2) and is_k and match_seq(buf, {2,1,4}, 15) then start_special(f, 3, btn_idx); return true end
    return false
  end
  if d.raw[7] and d.raw[8] and (d.p[7] or d.p[8]) then start_special(f, 2, 3); return true end
  if cid==7 and is_p and has_360(buf) then start_special(f, 1, btn_idx); return true end
  if (cid==1 or cid==2 or cid==11) and is_p and (match_seq(buf, {6,2,{2,3,6}}, 15) or match_seq(buf, {3,2,3}, 14)) then start_special(f, 2, btn_idx); return true end
  if cid==8 and is_k and (match_seq(buf,{6,2,{2,3,6}},15) or match_seq(buf,{4,2,{2,1,4}},15)) then start_special(f, 3, btn_idx); return true end
  if (f.chg_d>0 or f.chg_d_keep>0) and buf[1]>=7 then
    if (cid==3 or cid==4 or cid==5 or cid==6 or cid==10 or cid==12) and is_k then
      f.chg_d=0; f.chg_d_keep=0; start_special(f, (cid==4 or cid==10) and 2 or 3, btn_idx); return true
    elseif cid==9 and (is_p or is_k) then
      f.chg_d=0; f.chg_d_keep=0; start_special(f, 3, btn_idx); return true
    end
  end
  if (f.chg_b>0 or f.chg_b_keep>0) and (buf[1]==3 or buf[1]==6 or buf[1]==9) then
    if (cid==3 or cid==4 or cid==5 or cid==9 or cid==10 or cid==12) and is_p then
      f.chg_b=0; f.chg_b_keep=0; start_special(f, 1, btn_idx); return true
    elseif cid==6 and is_p then
      f.chg_b=0; f.chg_b_keep=0; start_special(f, 2, btn_idx); return true
    elseif (cid==9 or cid==12) and is_k then
      f.chg_b=0; f.chg_b_keep=0; start_special(f, 2, btn_idx); return true
    end
  end
  if match_seq(buf, {2,{2,3},6}, 15) then
    if (cid==1 or cid==2 or cid==8) and is_p then start_special(f, 1, btn_idx); return true
    elseif cid==11 and (is_p or is_k) then start_special(f, 1, btn_idx); return true
    elseif cid==7 and is_p then start_special(f, 2, btn_idx); return true end
  end
  if match_seq(buf, {2,{2,1},4}, 15) then
    if (cid==1 or cid==2 or cid==10 or cid==11 or cid==7) and is_k then start_special(f, 3, btn_idx); return true
    elseif cid==4 and is_p then start_special(f, 3, btn_idx); return true
    elseif cid==8 and is_p then start_special(f, 2, btn_idx); return true end
  end
  if cid==3 and is_k and #f.mash_k>=4 then f.mash_k={}; start_special(f, 2, btn_idx); return true end
  if cid==5 and is_p and #f.mash_p>=4 then f.mash_p={}; start_special(f, 2, btn_idx); return true end
  if cid==6 and is_p and #f.mash_p>=4 then f.mash_p={}; start_special(f, 1, btn_idx); return true end
  return false
end

local function try_throw(f, opp)
  if not opp or opp.y<FLOOR_Y-4 or opp.throw_invuln>0 or opp.st==FS_HIT or opp.st==FS_KD or opp.st==FS_WAKE then return false end
  if abs(f.x - opp.x) > 26 then return false end
  local d = inp[f.slot]
  local chord = d.raw[5] and d.raw[6] and (d.p[5] or d.p[6])
  local dir = get_rel_dir(f.slot, f.facing)
  local dir_h = (dir==6 or dir==4) and (d.p[7] or d.p[8])
  if not (chord or dir_h) then return false end
  sfx_play(9, 28, 16, 2)
  f.st=FS_THROW; f.st_t=0; f.vx=0
  local td = (dir==4) and -f.facing or f.facing
  f.facing = td
  opp.st=FS_KD; opp.st_t=0; opp.atk=nil
  opp.hp=max(0, opp.hp-14); opp.stun=min(120, opp.stun+12)
  opp.vy=-3.4; opp.vx=td*2.8
  opp.x=max(18, min(STG_W-18, f.x+td*18))
  add_shake(2, 8); spawn_fx("HIT", opp.x, opp.y-18, 9, 12); spawn_popup("THROW!", opp.x, opp.y-38, 9)
  if f.slot==1 then p1_score = p1_score + 500 end
  return true
end

local function run_ai(f, opp)
  local d = inp[f.slot]
  for b=1,8 do d.prev[b]=d.raw[b]; d.raw[b]=false end
  local dx = opp.x - f.x
  local dist = abs(dx)
  local toward = dx>=0 and 4 or 3
  local away = dx>=0 and 3 or 4
  if game_mode == 3 and not is_attract then
    if trn_guard == 2 then d.raw[away] = true elseif trn_guard == 3 then d.raw[away] = true; d.raw[2] = true end
    for b=1,8 do d.p[b]=d.raw[b] and not d.prev[b]; d.r[b]=not d.raw[b] and d.prev[b] end
    return
  end
  f.cpu_t = f.cpu_t + 1
  local aggr = is_attract and 1.1 or (0.65 + arcade_idx*0.04)
  local danger = (opp.st==FS_ATTACK and dist<44)
  for _, pr in ipairs(projs) do if pr.owner~=f.slot and abs(pr.x-f.x)<62 then danger=true end end
  if danger and rand()<0.72 then
    if f.cpu_t%12<6 then d.raw[away]=true; d.raw[2]=(rand()<0.4) else d.raw[1]=true; d.raw[toward]=true end
  elseif dist > 95 then
    if (f.cid==1 or f.cid==2 or f.cid==8 or f.cid==11) and rand()<0.045*aggr then start_special(f, 1, rand()<0.5 and 1 or 3)
    elseif rand()<0.65 then d.raw[toward]=true; if rand()<0.03 then d.raw[1]=true end end
  elseif dist > 42 then
    if rand()<0.55 then d.raw[toward]=true else d.raw[away]=true end
    if rand()<0.05*aggr then d.raw[rand()<0.5 and 6 or 8]=true elseif rand()<0.025*aggr then start_special(f, rand(1,3), 3) end
  else
    if opp.y<FLOOR_Y-12 and (f.cid==1 or f.cid==2 or f.cid==4 or f.cid==11) and rand()<0.08*aggr then start_special(f, 2, 3)
    elseif rand()<0.10*aggr then d.raw[rand(5,8)]=true; if rand()<0.45 then d.raw[2]=true end
    elseif rand()<0.04*aggr then start_special(f, rand(1,3), 3)
    elseif rand()<0.35 then d.raw[away]=true end
  end
  for b=1,8 do
    d.p[b]=d.raw[b] and not d.prev[b]; d.r[b]=not d.raw[b] and d.prev[b]
    d.hold[b]=d.raw[b] and (d.hold[b]+1) or 0
  end
end

local function check_block(def, atk, att_x)
  if def.y<FLOOR_Y-1 or def.st==FS_HIT or def.st==FS_KD or def.st==FS_DIZZY or def.st==FS_ATTACK or def.st==FS_THROW or def.st==FS_PREJUMP then return false end
  local atk_side = (att_x >= def.x) and 1 or -1
  local r = inp[def.slot].raw
  local holding_back = (atk_side==1 and r[3]) or (atk_side==-1 and r[4])
  if not holding_back then return false end
  if atk.low and not r[2] then return false end
  if atk.over and r[2] then return false end
  return true
end

local function resolve_hit(att, def, atk, att_x)
  local blocked = (not atk.grab) and check_block(def, atk, att_x)
  local old_face, was_atk = def.facing, (def.st==FS_ATTACK)
  local is_corner = (def.x<=24 and att_x>def.x) or (def.x>=STG_W-24 and att_x<def.x)
  local push = atk.push or 10
  if blocked then
    sfx_play(5, 40, 10, 2)
    def.st = inp[def.slot].raw[2] and FS_BLOCK_C or FS_BLOCK_S
    def.blockstun_t=12; def.atk=nil; def.facing=(att_x>=def.x) and 1 or -1
    if (atk.chip or 0)>0 then def.hp=max(1, def.hp-atk.chip) end
    hitstop = max(hitstop, (atk.hitstop or 7) - 2)
    spawn_fx("BLOCK", (att_x+def.x)*0.5, def.y-20, 14, 10)
    if is_corner then att.x=max(16, min(STG_W-16, att.x+(att.x<def.x and -push or push)))
    else def.x=max(16, min(STG_W-16, def.x+(att_x<def.x and push or -push))) end
  else
    local is_heavy = (atk.dmg >= 11)
    sfx_play(is_heavy and 4 or 3, is_heavy and 28 or 36, 12, 2)
    def.atk=nil; def.facing=(att_x>=def.x) and 1 or -1
    if not first_hit_done then
      first_hit_done = true
      spawn_popup("1ST ATTACK!", att.x, att.y-42, 4)
      if att.slot==1 then p1_score = p1_score + 500 end
    end
    if def.st==FS_HIT or def.st==FS_DIZZY then
      att.combo_cnt = att.combo_cnt + 1; att.combo_show_t = 65
      spawn_popup(att.combo_cnt.." HIT COMBO!", att.x, att.y-44, 9)
    else att.combo_cnt = 1 end
    local scale = max(0.5, 1.0 - (att.combo_cnt - 1)*0.15)
    local dmg = max(1, floor(atk.dmg * scale))
    if was_atk then
      dmg = dmg + 2
      spawn_popup("COUNTER!", def.x, def.y-40, 9)
      if att.slot==1 then p1_score = p1_score + 250 end
    elseif att.y < FLOOR_Y-2 and (att_x - def.x)*old_face < -2 and def.st~=FS_DIZZY then
      spawn_popup("CROSS-UP!", att.x, att.y-46, 4)
      if att.slot==1 then p1_score = p1_score + 300 end
    end
    def.hp = max(0, def.hp - dmg)
    def.stun = def.stun + (atk.stun or 10); def.stun_decay = 110
    hitstop = max(hitstop, atk.hitstop or 7)
    add_shake(is_heavy and 2 or 1, is_heavy and 8 or 4)
    spawn_fx("HIT", def.x, def.y-20, is_heavy and 8 or 9, 12)
    if att.slot==1 then p1_score = p1_score + dmg*25 end
    if def.hp <= 0 then
      def.st=FS_KD; def.vy=-3.8; def.vx=(att_x<def.x and 2.5 or -2.5)
      sfx_play(8, 24, 24, 3); add_shake(4, 18)
    elseif atk.kd or def.y<FLOOR_Y-1 then
      def.st=FS_KD; def.st_t=0; def.vy=-3.2; def.vx=(att_x<def.x and 2.2 or -2.2)
    elseif def.stun >= 100 and def.st ~= FS_DIZZY then
      def.stun=0; def.st=FS_DIZZY; def.st_t=0; def.dizzy_t=150
      sfx_play(10, 50, 16, 3); spawn_popup("DIZZY!", def.x, def.y-46, 9)
    else
      def.st=FS_HIT; def.st_t=0; def.hitstun_t = is_heavy and 18 or 13
    end
    if is_corner and def.y>=FLOOR_Y then att.x=max(16, min(STG_W-16, att.x+(att.x<def.x and -push or push)))
    elseif def.y>=FLOOR_Y then def.x=max(16, min(STG_W-16, def.x+(att_x<def.x and push or -push))) end
  end
  if atk.stomp then att.vy=-3.9; att.vx=-att.facing*1.2; att.atk=nil; att.st=FS_JUMP end
end

local function update_fighter(f, opp)
  if f.invuln_t>0 then f.invuln_t=f.invuln_t-1 end
  if f.throw_invuln>0 then f.throw_invuln=f.throw_invuln-1 end
  if f.proj_invuln>0 then f.proj_invuln=f.proj_invuln-1 end
  if f.wake_t>0 then f.wake_t=f.wake_t-1 end
  if f.combo_show_t>0 then f.combo_show_t=f.combo_show_t-1 end
  if f.red_hp>f.hp then f.red_hp=max(f.hp, f.red_hp-0.6) end
  if f.stun>0 then if f.stun_decay>0 then f.stun_decay=f.stun_decay-1 else f.stun=max(0, f.stun-0.25) end end
  local d = inp[f.slot]
  local dir = get_rel_dir(f.slot, f.facing)
  f.st_t = f.st_t + 1
  if opp and f.y>=FLOOR_Y and (f.st==FS_IDLE or f.st==FS_WALKF or f.st==FS_WALKB or f.st==FS_CROUCH) then
    if opp.x>f.x+2 then f.facing=1 elseif opp.x<f.x-2 then f.facing=-1 end
  end
  local atk_btn, is_neg = get_atk_trigger(f, true)
  if atk_btn==0 and f.buf_btn>0 and f.buf_btn_t>0 then atk_btn=f.buf_btn; is_neg=false; f.buf_btn=0; f.buf_btn_t=0
  elseif f.buf_btn_t>0 then f.buf_btn_t=f.buf_btn_t-1 end
  if f.st == FS_DIZZY then
    if d.p[5] or d.p[6] or d.p[7] or d.p[8] or d.p[3] or d.p[4] then f.dizzy_t=f.dizzy_t-4 end
    f.dizzy_t = f.dizzy_t - 1
    if f.dizzy_t <= 0 then f.st=FS_IDLE; f.st_t=0; f.wake_t=3 end
    return
  elseif f.st == FS_HIT then
    f.hitstun_t=f.hitstun_t-1; if f.hitstun_t<=0 then f.st=FS_IDLE; f.st_t=0; f.wake_t=3 end; return
  elseif f.st == FS_BLOCK_S or f.st == FS_BLOCK_C then
    f.blockstun_t=f.blockstun_t-1; if f.blockstun_t<=0 then f.st=d.raw[2] and FS_CROUCH or FS_IDLE; f.st_t=0; f.wake_t=3 end; return
  elseif f.st == FS_KD then
    f.x=f.x+f.vx; f.y=f.y+f.vy; f.vy=f.vy+GRAV
    if f.y >= FLOOR_Y then
      f.y=FLOOR_Y; f.vy=0; f.vx=f.vx*0.4
      if f.hp<=0 then f.st=FS_LOSE; return end
      if f.st_t>=26 then f.st=FS_WAKE; f.st_t=0; f.invuln_t=14 end
      for _, pr in ipairs(props) do
        if pr.hp>0 and abs(f.x-pr.x)<22 then pr.hp=0; sfx_play(8,36,12,3); spawn_fx("CRATE",pr.x,FLOOR_Y-10,6,18) end
      end
    end
    f.x=max(16, min(STG_W-16, f.x)); return
  elseif f.st == FS_WAKE then if f.st_t>=12 then f.st=FS_IDLE; f.st_t=0; f.wake_t=3 end; return
  elseif f.st == FS_THROW then if f.st_t>=18 then f.st=FS_IDLE; f.st_t=0 end; return
  elseif f.st == FS_PREJUMP then
    if atk_btn>0 and check_special_cmd(f, atk_btn, false) then return end
    if f.st_t>=2 then f.throw_invuln=2 end
    if f.st_t>=3 then f.st=FS_JUMP; f.st_t=0; f.vy=f.c.jvy; f.vx=f.pj_dir*f.c.jvx; sfx_play(2,46,6,1,7) end
    return
  elseif f.st == FS_JUMP then
    if atk_btn>0 and not is_neg and not f.atk then
      if not check_special_cmd(f, atk_btn, true) then sfx_play(2,36,6,1,7); f.atk=make_normal(f, atk_btn, false, true, dir) end
    end
    if f.atk then
      local a = f.atk
      a.on = (f.st_t >= a.startup and f.st_t < a.startup + a.active)
    end
    f.x=max(16, min(STG_W-16, f.x+f.vx)); f.y=f.y+f.vy; f.vy=f.vy+GRAV
    if f.y>=FLOOR_Y then
      f.y=FLOOR_Y; f.vy=0; f.vx=0; f.atk=nil
      f.st=d.raw[2] and FS_CROUCH or FS_IDLE; f.st_t=0
      spawn_fx("DUST", f.x, FLOOR_Y, 2, 8)
    end
    return
  elseif f.st == FS_ATTACK and f.atk then
    local a = f.atk
    if a.sp_fire and f.st_t == a.startup then
      spawn_proj(f, a.sp_kind or "HADOU", a.sp_spd, a.sp_dmg, a.sp_hy, f.pal[7], 1)
    end
    if f.vx~=0 and ((a.sp and a.sp>0) or (a.vx and f.st_t<a.startup+a.active)) then
      f.x=max(16, min(STG_W-16, f.x+f.vx))
      if not a.sp then f.vx=f.vx*0.84 end
      if a.sp and (f.y<FLOOR_Y or f.vy<0) then f.y=f.y+f.vy; f.vy=f.vy+GRAV; if f.y>=FLOOR_Y then f.y=FLOOR_Y; f.vy=0; f.vx=0 end end
    end
    if not a.sp and atk_btn>0 and (((f.cid==3 and #f.mash_k>=4) or ((f.cid==5 or f.cid==6) and #f.mash_p>=4))) then
      if check_special_cmd(f, atk_btn, false) then return end
    end
    if a.cancel and f.st_t>=a.startup and atk_btn>0 then
      if check_special_cmd(f, atk_btn, false) then return end
    end
    a.on = (f.st_t >= a.startup and f.st_t < a.startup + a.active)
    if f.st_t >= a.startup + a.active + a.rec then
      f.atk=nil; f.vx=0
      f.st = (f.y<FLOOR_Y) and FS_JUMP or (d.raw[2] and FS_CROUCH or FS_IDLE); f.st_t=0
    end
    return
  end

  if dir >= 7 then
    if atk_btn>0 and check_special_cmd(f, atk_btn, false) then return end
    f.st=FS_PREJUMP; f.st_t=0; f.pj_dir=(d.raw[4] and 1 or (d.raw[3] and -1 or 0)); f.vx=0; return
  end
  if atk_btn > 0 then
    if not is_neg and opp and try_throw(f, opp) then return end
    if check_special_cmd(f, atk_btn, false) then return end
    if not is_neg then
      sfx_play(2,34,6,1,7); f.st=FS_ATTACK; f.st_t=0
      f.atk=make_normal(f, atk_btn, d.raw[2], false, dir)
      f.vx=f.atk.vx and (f.facing*f.atk.vx) or 0
      return
    end
  end
  if d.raw[2] then f.st=FS_CROUCH; f.vx=0
  elseif dir==6 then f.st=FS_WALKF; f.vx=f.facing*f.c.spd_f; f.x=max(16, min(STG_W-16, f.x+f.vx))
  elseif dir==4 then f.st=FS_WALKB; f.vx=-f.facing*f.c.spd_b; f.x=max(16, min(STG_W-16, f.x+f.vx))
  else f.st=FS_IDLE; f.vx=0 end
end

local function resolve_collisions(f1, f2)
  if abs(f1.y - f2.y) < 20 then
    local dx = f2.x - f1.x
    if abs(dx) < 16 then
      local push = (16 - abs(dx)) * 0.5
      local sgn = dx>=0 and 1 or -1
      f1.x=max(16, min(STG_W-16, f1.x-sgn*push)); f2.x=max(16, min(STG_W-16, f2.x+sgn*push))
    end
  end
  local function box_overlap(att, def)
    local a = att.atk
    if not a or not a.on or a.dmg<=0 or (a.hit and not a.multi) then return false end
    if def.invuln_t>0 or def.st==FS_KD or def.st==FS_LOSE then return false end
    local hx1 = att.facing==1 and (att.x+4) or (att.x-4-a.reach)
    local hx2 = att.facing==1 and (att.x+4+a.reach) or (att.x-4)
    local hy1, hy2 = att.y+a.hy, att.y+a.hy+a.hh
    local dh = (def.st==FS_CROUCH or def.st==FS_BLOCK_C) and 22 or 34
    return hx1<=def.x+9 and hx2>=def.x-9 and hy1<=def.y and hy2>=def.y-dh
  end
  local h12, h21 = box_overlap(f1, f2), box_overlap(f2, f1)
  if h12 then
    if not f1.atk.multi then f1.atk.hit=true elseif f1.st_t%6~=0 then h12=false end
    if h12 then resolve_hit(f1, f2, f1.atk, f1.x) end
  end
  if h21 then
    if not f2.atk.multi then f2.atk.hit=true elseif f2.st_t%6~=0 then h21=false end
    if h21 then resolve_hit(f2, f1, f2.atk, f2.x) end
  end
  for i=#projs,1,-1 do
    local p = projs[i]
    p.x=p.x+p.vx; p.life=p.life-1
    if t%3==0 then spawn_fx("SPARK", p.x-p.vx*2, p.y, p.col2, 6) end
    local rm = (p.life<=0 or p.x<-12 or p.x>STG_W+12)
    if not rm then
      for j=i-1,1,-1 do
        local q = projs[j]
        if q.owner~=p.owner and abs(p.x-q.x)<12 and abs(p.y-q.y)<14 then
          spawn_fx("BLOCK",(p.x+q.x)*0.5,p.y,14,12); sfx_play(5,48,8,2); p.life=0; q.life=0; rm=true; break
        end
      end
    end
    if not rm then
      local def, att = (p.owner==1) and f2 or f1, (p.owner==1) and f1 or f2
      if def.proj_invuln==0 and def.invuln_t==0 and def.st~=FS_KD and def.st~=FS_LOSE then
        local dh = (def.st==FS_CROUCH or def.st==FS_BLOCK_C) and 20 or 34
        if abs(p.x-def.x)<12 and p.y>=def.y-dh and p.y<=def.y then
          resolve_hit(att, def, {dmg=p.dmg, chip=p.chip, stun=p.stun, push=10, hitstop=9}, p.x-p.vx*3); rm=true
        end
      end
    end
    if rm or p.life<=0 then table.remove(projs, i) end
  end
end

local function init_stage(sid)
  cur_stage=sid; props={{x=24,hp=1},{x=STG_W-24,hp=1}}; projs={}; fx={}; popups={}
end

local function start_round()
  local c1, c2, w1, w2, cpu2 = P1.cid, P2.cid, P1.wins, P2.wins, P2.is_cpu
  P1 = make_fighter(1, c1, is_attract, false)
  P2 = make_fighter(2, c2, cpu2, c1==c2)
  P1.wins=w1; P2.wins=w2; timer_sec=99; timer_sub=0; cam_x=40; hitstop=0; shake_t=0; first_hit_done=false
  round_over_t=0; ko_echo_t=0
  init_stage(P2.cid)
  match_banner = round_num==1 and "ROUND 1" or (round_num==2 and "ROUND 2" or "FINAL ROUND")
  match_banner_t=72; freeze_t=72; sfx_play(11,48,16,0); sync_music(STG_TRK[cur_stage] or 1)
end

local function start_match(c1, c2, mode)
  p1_pick=c1; p2_pick=c2; round_num=1
  P1 = make_fighter(1, c1, is_attract, false)
  P2 = make_fighter(2, c2, (mode==1 or mode==3 or is_attract), c1==c2)
  start_round()
end

local function start_car_bonus()
  state=ST_BONUS; P1=make_fighter(1, p1_pick, false, false); P1.x=76
  car={x=176, hp=100, max_hp=100, hit_t=0, time=20, sub=0, done=false}
  projs={}; fx={}; popups={}; cam_x=18; match_banner="BONUS STAGE!"; match_banner_t=50; sync_music(6)
end

local HEAD_TILES = {32,34,36,38,40,42,44,46,64,66,68,70}

local function draw_chibi_head(cid, sx, cy, dir, p, scale, flash, pain)
  local sc = scale or 1
  set_char_pal(p, flash)
  spr(HEAD_TILES[cid] or 32, floor(sx - 8*sc), floor(cy - 8*sc), 0, sc, dir==-1 and 1 or 0, 0, 2, 2)
  pal_reset()
  if pain and sc==1 and not flash then
    local ex = sx + dir*2
    pix(ex-1, cy-1, 0); pix(ex, cy, 0); pix(ex-1, cy+1, 0)
    pix(ex+3*dir, cy-1, 0); pix(ex+2*dir, cy, 0); pix(ex+3*dir, cy+1, 0)
  end
  if cid==1 and sc>=1 and not flash then
    local kx = floor(sx - dir*7*sc)
    local ky = floor(cy - 3*sc)
    local dy = (t%12<6) and 0 or sc
    rect(kx - (dir==1 and 3*sc or 0), ky+dy, 3*sc, 2*sc, p[5])
  end
end

local function draw_chibi_spr(cid, sx, fy, dir, p, sc, bid, crouch, flash, pain)
  local fl = dir==-1 and 1 or 0
  set_char_pal(p, flash)
  spr(bid, floor(sx - 12*sc), floor(fy - 16*sc), 0, sc, fl, 0, 3, 2)
  pal_reset()
  if bid == 192 then return end
  if bid == 172 then
    draw_chibi_head(cid, sx - dir*8*sc, fy - 10*sc, dir, p, sc, flash, pain)
    return
  end
  local hy = crouch and (fy - 18*sc) or (fy - 22*sc)
  local hx = sx
  if bid == 131 or bid == 134 or bid == 160 then hx = sx - dir*2*sc
  elseif bid == 169 then hy = fy - 23*sc end
  draw_chibi_head(cid, hx, hy, dir, p, sc, flash, pain)
end

local function draw_stage(sid, cx)
  local skies = {7,12,12,12,11,12,0,8,0,6,8,15}
  local floors = {5,6,3,3,11,13,3,5,3,6,5,3}
  cls(skies[sid] or 13)
  local px1, px2 = floor(-cx*0.35), floor(-cx*0.7)
  if sid==1 then -- RYU: Suzaku Castle Sunset + Furinkazan Board & Sakura Petals
    rect(0,0,240,34,13); dither_seam(28,8); rect(0,34,240,28,8); dither_seam(54,7); rect(0,62,240,36,7); dither_seam(88,1)
    circ(px1+44,30,10,9); circ(px1+44,30,7,1)
    rect(px1+10,20,34,4,8); rect(px1+170,26,40,4,8)
    tri(px1+0,98,px1+45,68,px1+105,98,3); tri(px1+140,98,px1+210,64,px1+260,98,3)
    out_rect(px1+78,60,104,38,1); out_rect(px1+92,38,76,22,1)
    tri(px1+66,60,px1+130,48,px1+194,60,3); tri(px1+80,38,px1+130,18,px1+180,38,3)
    for rx=0,11 do spr(14, px1+84+rx*8, 52, 0) end
    for rx=0,7 do spr(14, px1+98+rx*8, 30, 0) end
    rect(px1+124,14,12,4,9); rect(px1+100,19,4,6,9); rect(px1+156,19,4,6,9)
    rect(px1+108,68,44,30,6); rect(px1+114,72,32,26,0); rect(px1+122,43,16,12,7)
    rect(px1+22,42,8,56,6)
    for sx=-1,2 do spr(16, px1+16+sx*7, 30+(sx%2)*5, 0); spr(16, px1+18+sx*6, 38, 0) end
    out_rect(px2+192,42,12,54,6); rectb(px2+192,42,12,54,9)
    for k=0,3 do rect(px2+195,46+k*12,6,2,9); rect(px2+196,49+k*12,4,5,9) end
    for p=0,5 do pix((p*43+floor(t*0.7))%240,(p*23+floor(t*0.5))%92,7) end
  elseif sid==2 then -- KEN: Harbor Dock, Cargo Crane & SS Freedom Yacht
    rect(0,0,240,46,12); dither_seam(40,14); rect(0,46,240,26,14); dither_seam(64,12)
    rect(0,72,240,26,13)
    for g=0,2 do
      local gx, gy = (px1+50+g*68+floor(t*0.25))%240, 14+(g%2)*8
      local wf = (t%16<8) and -1 or 1
      line(gx-3,gy+wf,gx,gy,1); line(gx,gy,gx+3,gy+wf,1)
    end
    for i=0,10 do spr(17, px1+i*24+(floor(t/14)%6), 72+(i%2)*2, 0) end
    rectb(px2+18,44,12,54,7); line(px2+18,44,px2+29,68,7); line(px2+29,68,px2+18,96,7)
    out_rect(px2+15,40,18,6,7); line(px2+24,40,px2+50,22,7); line(px2+50,22,px2+50,42,2)
    out_rect(px2+112,56,124,22,1); rect(px2+112,72,124,6,7); rect(px2+114,52,120,4,9)
    out_rect(px2+136,38,72,18,1); rect(px2+142,42,24,8,14); rect(px2+170,42,20,8,14); rect(px2+194,42,10,8,0)
    for p_i=0,4 do circ(px2+124+p_i*20,64,3,13); circ(px2+124+p_i*20,64,2,14) end
    rect(px2+168,18,3,20,2); rect(px2+171,20,16,8,7); rect(px2+171,20,7,4,13); rect(px2+156,28,28,2,1)
  elseif sid==3 then -- CHUN-LI: Taiping Market Street & Swaying Lanterns
    rect(0,0,240,36,12); dither_seam(30,14); rect(0,36,240,62,2)
    for i=0,4 do
      local bx = px1+i*56
      out_rect(bx,22,50,76,i%2==0 and 5 or 3); tri(bx-2,22,bx+25,10,bx+52,22,7)
      rect(bx+8,32,12,18,0); rect(bx+30,32,12,18,0); rect(bx+6,58,38,4,9)
      out_rect(bx+20,18,10,22,i%2==0 and 7 or 11); circ(bx+8,26,4,7); circ(bx+42,26,4,7)
    end
    line(0,14,240,18,0)
    for i=0,5 do
      local lx = 20+i*40+floor(sin(t*0.07+i)*2)
      line(lx,15,lx,19,0); out_circ(lx,22,3,7); pix(lx,22,9)
    end
  elseif sid==4 then -- GUILE: Air Force Base F-16 & Chain Fence
    rect(0,0,240,38,12); dither_seam(32,14); rect(0,38,240,36,14)
    rect(0,74,240,24,11); dither_seam(74,10)
    for fx=0,240,16 do line(fx,74,fx+8,98,2) end; line(0,74,240,74,2)
    out_rect(px1+18,34,20,64,2); rect(px1+14,24,28,12,3); rect(px1+16,26,24,6,14)
    local rx = px1+28+floor(cos(t*0.1)*5)
    line(px1+28,24,px1+28,12,1); circb(rx,13,3,9)
    out_rect(px2+82,62,128,16,2); rect(px2+82,70,128,8,3)
    tri(px2+54,70,px2+82,62,px2+82,78,3); rect(px2+64,74,10,2,1)
    tri(px2+102,62,px2+124,48,px2+150,62,14)
    tri(px2+176,62,px2+204,26,px2+212,62,2); rect(px2+196,40,8,6,9); pix(px2+200,43,1)
    rect(px2+110,80,6,14,0); rect(px2+174,80,6,14,0); circ(px2+113,94,4,0); circ(px2+177,94,4,0)
  elseif sid==5 then -- BLANKA: Amazon River Stilt Hut & Giant Anaconda
    rect(0,0,240,42,11); dither_seam(36,10); rect(0,42,240,32,10); rect(0,74,240,24,12)
    for i=0,7 do rect(px1+i*36,0,6,74,6); circ(px1+i*36+3,12+(i%2)*6,16,11); line(px1+i*36+12,0,px1+i*36+16,52,10) end
    rect(px1+56,12,124,5,6)
    for c=0,4 do out_circ(px2+104+c*8,16-(c%2)*2,5,10); pix(px2+104+c*8,15-(c%2)*2,9) end
    out_circ(px2+144,20,6,10); pix(px2+146,18,7); line(px2+150,21,px2+154+(t%8<4 and 2 or 0),21,7)
    out_rect(px2+88,42,76,34,6); tri(px2+76,42,px2+126,18,px2+176,42,8); rect(px2+106,52,24,24,0); rect(px2+96,76,6,22,6); rect(px2+152,76,6,22,6)
  elseif sid==6 then -- E.HONDA: Sentou Bathhouse, Rising Sun Mural & Steam
    rect(0,0,240,98,14); rect(0,0,240,24,12); dither_seam(18,14)
    for r=0,5 do line(px1+124,58,px1+24+r*40,24,7) end
    tri(px1+44,78,px1+124,18,px1+204,78,13); tri(px1+100,36,px1+124,18,px1+148,36,1)
    circ(px1+194,26,9,7)
    out_rect(px2+192,28,26,26,13); circb(px2+205,41,6,1); line(px2+205,34,px2+205,49,1)
    for i=0,14 do rect(px1+i*18,78,16,10,12); rectb(px1+i*18,78,16,10,1) end
    out_rect(0,88,240,12,8); dither_seam(84,1)
    for s=0,4 do circb(px2+40+s*38,82-((t+s*7)%18),2,1) end
  elseif sid==7 then -- ZANGIEF: Steel Foundry & Molten Ladle
    rect(0,0,240,98,0); rect(0,72,240,26,6); dither_seam(68,7)
    for i=0,4 do rect(px1+i*58,0,10,98,3); rectb(px1+i*58,0,10,98,2) end
    rect(0,22,240,6,3); rect(114,18,12,12,7); pix(120,24,9)
    line(px2+70,28,px2+70,60,2); line(px2+180,28,px2+180,56,2)
    out_rect(px2+114,24,20,14,2); rect(px2+121,38,6,28,(t%6<3) and 9 or 8); circ(px2+124,68,4,(t%4<2) and 9 or 1)
    out_rect(px2+88,52,72,42,3); rect(px2+94,54,60,14,(t%10<5) and 9 or 8); circ(px2+110+(t%24),50-(t%18),2,9)
  elseif sid==8 then -- DHALSIM: Elephant Temple & Swaying Trunks
    rect(0,0,240,36,7); dither_seam(30,8); rect(0,36,240,62,8)
    for i=0,3 do
      local ex = px1+i*76
      local sw = floor(sin(t*0.08+i)*3)
      out_rect(ex+8,24,38,74,5); rect(ex+12,28,30,10,9)
      out_circ(ex+27,54,12,2); rect(ex+23,54,8,14,2); rect(ex+23+sw,66,8,10,2)
      line(ex+19,58,ex+11,64,1); line(ex+35,58,ex+43,64,1); circ(ex+27,48,3,7)
    end
  elseif sid==9 then -- BALROG: Las Vegas Neon Casino & Classic Pink Cruiser
    rect(0,0,240,98,0); for s=0,14 do pix((s*53)%240,(s*19)%38,1) end
    for i=0,5 do
      local nx = px1+i*46
      out_rect(nx,20+(i%2)*14,38,78,i%2==0 and 15 or 13)
      for w=0,3 do rect(nx+6,26+(i%2)*14+w*14,26,6,((floor(t/8)+i+w)%2==0) and 9 or 7) end
    end
    out_rect(px2+82,56,84,42,7); rect(px2+88,62,72,14,0); print("CASINO",px2+102,66,9,true,1,false)
    for b=0,11 do pix(px2+84+b*7,58,((floor(t/4)+b)%2==0) and 9 or 1) end
    out_rect(px2+16,78,56,16,7); rect(px2+26,70,32,9,1); rect(px2+30,72,24,5,14)
    out_circ(px2+28,94,4,0); out_circ(px2+60,94,4,0); rect(px2+16,84,56,3,1)
  elseif sid==10 then -- VEGA: Flamenco Brick Tavern, Steel Cage & Rose Petals
    rect(0,0,240,98,6); dither_seam(48,0)
    for rx=0,29 do for ry=2,7 do spr(15, (px1%8)+rx*8, ry*8, 0) end end
    for i=0,3 do local ax=px1+20+i*64; rect(ax,34,36,64,0); rectb(ax,34,36,64,9); circ(ax+18,34,18,0); circb(ax+18,34,18,9) end
    for gx=36,204,12 do line(gx,16,gx+12,96,3) end
    rectb(36,16,168,82,2); rectb(37,17,166,80,3)
    for r=0,3 do pix((r*61+floor(t*0.6))%240,(r*29+floor(t*0.5))%90,7) end
  elseif sid==11 then -- SAGAT: Reclining Buddha Ruins & Lotus Pedestal
    rect(0,0,240,36,8); dither_seam(30,9); rect(0,36,240,34,9); rect(0,70,240,28,7)
    tri(px1+12,72,px1+36,42,px1+60,72,6); tri(px1+180,72,px1+212,40,px1+244,72,6)
    out_rect(px1+44,74,160,24,9); out_rect(px1+56,64,120,12,8); out_circ(px1+62,64,14,9); circ(px1+62,48,4,9)
    pix(px1+60,60,0); line(px1+56,66,px1+64,66,8)
    rect(px1+76,72,96,6,8); line(px1+84,78,px1+168,78,6)
    for l=0,9 do tri(px1+46+l*16,98,px1+54+l*16,88,px1+62+l*16,98,8) end
  else -- M.BISON: Shadaloo Naga Temple & Ornate Golden Bell
    rect(0,0,240,42,0); dither_seam(36,15); rect(0,42,240,56,15)
    for i=0,4 do rect(px1+i*58,14,14,84,3); rect(px1+i*58-2,14,18,6,9); rectb(px1+i*58,14,14,84,0) end
    out_rect(px2+98,28,52,54,3); circb(px2+124,54,20,9); rect(px2+114,44,20,18,0)
    out_circ(px2+124,46,12,9); out_rect(px2+112,46,24,22,9); rect(px2+108,66,32,5,8)
    out_circ(px2+86,28,5,10); out_circ(px2+162,28,5,10)
    spr(236, px2+116, 46, 0)
  end
  -- Cheering Pixel-Art Spectators (tiles 202 & 204)
  local bob = (t%20<10) and 0 or 1
  for i=0,3 do
    local sx = px2 + 38 + i*64
    if sx>-18 and sx<258 then
      pal_remap(15, 0)
      spr(i%2==0 and 202 or 204, sx, 83-bob, 0, 1, i%2, 0, 2, 2)
      pal_reset()
    end
  end
  -- Textured Perspective Stage Floor
  rect(0,98,240,38,floors[sid] or 3); dither_seam(98,0)
  line(0,98,240,98,0); line(0,99,240,99,2); line(0,111,240,111,0); line(0,124,240,124,0)
  for i=-2,12 do local lx=floor(i*30-(cx%30)); line(lx,99,lx-14,136,0) end
  -- Destructible Stage-Themed Props (16x16 tile 78)
  for _, pr in ipairs(props) do
    if pr.hp>0 then
      pal_remap(15,0)
      if sid==4 or sid==7 or sid==9 then pal_remap(6,3); pal_remap(8,2)
      elseif sid==1 or sid==8 or sid==12 then pal_remap(6,7); pal_remap(8,9) end
      spr(78, floor(pr.x-cx)-8, FLOOR_Y-16, 0, 1, 0, 0, 2, 2); pal_reset()
    end
  end
end

local function is_kick(a, cid)
  if cid==10 and a.sp==3 then return true end
  return a.name:find("KICK") or a.name:find("LK") or a.name:find("HK") or a.name:find("KNEE") or a.name:find("STOMP") or a.name:find("TATSU") or a.name:find("SCISSOR") or a.name:find("BIRD")
end

local function draw_fighter(f, cx)
  if f.invuln_t>0 and (t%4<2) then return end
  local sx, sy, dir, p = floor(f.x-cx), floor(f.y), f.facing, f.pal
  local crouch = (f.st==FS_CROUCH or f.st==FS_BLOCK_C or f.st==FS_PREJUMP)
  if f.y <= FLOOR_Y then
    local sh = max(8, 13-floor((FLOOR_Y-f.y)/6))
    rect(sx-sh, FLOOR_Y, sh*2, 2, 0)
  end
  if f.st==FS_KD or f.st==FS_LOSE then
    draw_chibi_spr(f.cid, sx, sy, dir, p, 1, 172, false, false, true)
    return
  end
  local atk = f.atk
  local act = ((f.st==FS_ATTACK or f.st==FS_JUMP) and atk and atk.on)
  local bid = (f.cid==3 and 163 or ((f.cid==5 or f.cid==6 or f.cid==7) and 166 or (t%28<14 and 96 or 99)))
  if f.st==FS_WALKF or f.st==FS_WALKB then
    bid = (t%12<6) and 102 or (f.cid==3 and 163 or 96)
  elseif crouch then
    bid = 105
  elseif f.st==FS_WIN then
    bid = (f.cid==3 and 195 or 128)
  elseif f.st==FS_BLOCK_S or f.st==FS_BLOCK_C then
    bid = 140
  elseif f.st==FS_HIT or f.st==FS_DIZZY then
    bid = 160
  elseif f.y<FLOOR_Y-1 then
    bid = (act and f.cid==3) and 195 or 137
  elseif f.st==FS_ATTACK and atk then
    if (f.cid==5 and (atk.sp==1 or atk.sp==3)) or (f.cid==12 and atk.sp==1) then
      bid = 192
    elseif atk.name:find("UPPER") or atk.name:find("SHORYU") or atk.name:find("FLASH") or atk.name:find("HEAD") then
      bid = 128
    elseif atk.name:find("TATSU") or atk.name:find("LARIAT") or atk.name:find("BIRD") or atk.name:find("SCISSOR") then
      bid = (f.cid==3 and 195 or 169)
    elseif atk.low then
      bid = 134
    elseif is_kick(atk, f.cid) then
      bid = (f.cid==3 and 195 or 131)
    else
      bid = ((f.cid==6 or f.cid==7) and 198 or 108)
    end
  end

  if f.st==FS_ATTACK and atk and atk.sp and atk.sp>0 then
    if (f.cid==5 and atk.sp==2) or (f.cid==12 and atk.sp==1) or (f.cid==7 and atk.sp==2) then
      circb(sx, sy-16, 15+(t%3)*2, p[7]); circb(sx, sy-16, 13+(t%2)*2, 1)
    end
    if f.cid==12 and atk.sp==1 then
      tri(sx+dir*22, sy-14, sx-dir*8, sy-24, sx-dir*8, sy-4, 15)
      tri(sx+dir*18, sy-14, sx-dir*4, sy-20, sx-dir*4, sy-8, 14)
    end
    if f.cid==4 and atk.sp==2 then
      pal_remap(12,9); pal_remap(14,1)
      spr(74, sx+dir*2-8, sy-38, 0, 1, dir==-1 and 1 or 0, 0, 2, 2)
      pal_reset()
      line(sx-dir*6, sy-28, sx+dir*16, sy-42, 9)
    end
    if atk.name:find("TATSU") or atk.name:find("BIRD") or atk.name:find("SCISSOR") then
      ellib(sx, sy-15, 16, 4, (t%4<2) and 1 or 14)
      ellib(sx, sy-9, 13, 3, 14)
    end
  elseif f.st==FS_THROW then
    circb(sx+dir*14, sy-16, 6+(f.st_t%5), 9)
    spr(76, sx+dir*6, FLOOR_Y-16, 0, 1, 0, 0, 2, 2)
  end

  local flash = (f.st==FS_HIT and f.st_t<=3)
  draw_chibi_spr(f.cid, sx, sy, dir, p, 1, bid, crouch, flash, f.st==FS_HIT or f.st==FS_DIZZY)

  if act and atk.reach >= 14 then
    local fl = dir==-1 and 1 or 0
    local tip = min(28, atk.reach)
    local ay = crouch and (sy-13) or (atk.low and (sy-9) or (sy-19))
    if f.cid==8 then
      set_char_pal(p, flash)
      for s_i=1,floor((tip-8)/7) do spr(21, sx+dir*(6+s_i*7)-4, ay, 0, 1, fl) end
      spr(22, sx+dir*(4+tip)-4, ay, 0, 1, fl)
      pal_reset()
    elseif f.cid==10 and not is_kick(atk, f.cid) then
      pal_remap(15,0); spr(23, sx+dir*15-4, ay, 0, 1, fl); pal_reset()
    elseif atk.multi then
      pal_remap(15,0)
      for m=-1,1 do spr(is_kick(atk,f.cid) and 19 or 18, sx+dir*(13+(t+m)%4)-4, ay+m*4, 0, 1, fl) end
      pal_reset()
    elseif (f.cid==1 or f.cid==2 or f.cid==11) and atk.sp==2 then
      pal_remap(15,0)
      if f.cid==1 then pal_remap(8,13); pal_remap(9,14) end
      spr(238, sx+dir*8-8, sy-34, 0, 1, fl, 0, 2, 2)
      pal_reset()
    elseif is_kick(atk, f.cid) then
      pal_remap(15,0); spr(19, sx+dir*15-4, ay, 0, 1, fl); pal_reset()
    else
      pal_remap(15,0); spr(atk.over and 20 or 18, sx+dir*14-4, ay, 0, 1, fl); pal_reset()
    end
  end

  if f.st==FS_DIZZY then
    for i=1,3 do local ang=t*0.2+i*2.1; spr(i%2==0 and 7 or 8, sx+floor(cos(ang)*10)-4, sy-34+floor(sin(ang)*3), 0) end
  end
end

local function draw_flag(cid, x, y)
  if cid==1 or cid==6 then out_rect(x,y,12,8,1); rect(x+4,y+2,4,4,7)
  elseif cid==2 or cid==4 or cid==9 then out_rect(x,y,12,8,1); rect(x,y+1,12,2,7); rect(x,y+5,12,2,7); rect(x,y,5,4,13)
  elseif cid==3 then out_rect(x,y,12,8,7); rect(x+1,y+1,3,3,9); pix(x+5,y+2,9)
  elseif cid==5 then out_rect(x,y,12,8,10); tri(x+1,y+4,x+6,y+1,x+6,y+7,9); tri(x+11,y+4,x+6,y+1,x+6,y+7,9); rect(x+5,y+3,2,2,13)
  elseif cid==7 then out_rect(x,y,12,8,7); rect(x+1,y+1,3,3,9); pix(x+2,y+2,7)
  elseif cid==8 then out_rect(x,y,12,8,1); rect(x,y,12,3,8); rect(x,y+5,12,3,10); rect(x+5,y+3,2,2,13)
  elseif cid==10 then out_rect(x,y,12,8,7); rect(x,y+2,12,4,9); pix(x+3,y+3,7)
  else out_rect(x,y,12,8,7); rect(x,y+2,12,4,1); rect(x,y+3,12,2,13) end
end

local function draw_fight_hud()
  rect(4,3,16,16,P1.pal[3]); rectb(3,2,18,18,1); draw_chibi_head(P1.cid,12,11,1,P1.pal,1,false)
  rect(220,3,16,16,P2.pal[3]); rectb(219,2,18,18,1); draw_chibi_head(P2.cid,228,11,-1,P2.pal,1,false)
  local bw = 82
  rect(22,4,bw,6,7); rectb(21,3,bw+2,8,1)
  local r1, w1 = floor((P1.red_hp/P1.max_hp)*bw), floor((P1.hp/P1.max_hp)*bw)
  if r1>w1 then rect(22+bw-r1,4,r1-w1,6,8) end
  if w1>0 then rect(22+bw-w1,4,w1,6,9) end
  rect(136,4,bw,6,7); rectb(135,3,bw+2,8,1)
  local r2, w2 = floor((P2.red_hp/P2.max_hp)*bw), floor((P2.hp/P2.max_hp)*bw)
  if r2>w2 then rect(136+w2,4,r2-w2,6,8) end
  if w2>0 then rect(136,4,w2,6,9) end
  rect(21,11,84,8,0); rectb(21,11,84,8,15); print(P1.c.name,23,13,1,true,1,true)
  rect(66,13,36,4,15); local sw1=min(36,floor(36*P1.stun/100))
  if sw1>0 then rect(66,13,sw1,4,(P1.stun>=75 or P1.st==FS_DIZZY) and ((t%4<2) and 7 or 8) or 9) end
  rect(135,11,84,8,0); rectb(135,11,84,8,15); print(P2.c.name,217-#P2.c.name*4,13,1,true,1,true)
  rect(138,13,36,4,15); local sw2=min(36,floor(36*P2.stun/100))
  if sw2>0 then rect(138+36-sw2,13,sw2,4,(P2.stun>=75 or P2.st==FS_DIZZY) and ((t%4<2) and 7 or 8) or 9) end
  rect(108,2,24,10,0); rectb(108,2,24,10,9); print("KO",114,4,7,true,1,false)
  rect(111,12,18,8,0); rectb(111,12,18,8,15); print(string.format("%02d",timer_sec),114,13,timer_sec<=15 and 7 or 9,true,1,false)
  for i=1,P1.wins do spr(9,80+(i-1)*9,21,0) end
  for i=1,P2.wins do spr(9,210-(i-1)*9,21,0) end
  if game_mode==1 then
    rect(21,20,56,8,0); rectb(21,20,56,8,15); print(string.format("SCORE %06d",p1_score),23,22,14,true,1,true)
  elseif game_mode==3 then
    rect(21,20,78,8,0); rectb(21,20,78,8,15); print("TRAINING // TAB:BOX",23,22,14,true,1,true)
    local gn={"IDLE","AUTO","LOW"}
    rect(135,20,84,8,0); rectb(135,20,84,8,15); print("R:GRD-"..gn[trn_guard].." ST:"..floor(P2.stun),137,22,9,true,1,true)
    for i=1,min(7,#inp[1].log) do
      local e=inp[1].log[i]; print(DIR_GLYPHS[e.dir]..(e.atk~="" and ("+"..e.atk) or ""),4,29+(i-1)*7,1,true,1,true)
    end
    if show_hitboxes then
      for _, f in ipairs({P1,P2}) do
        local fs = floor(f.x-cam_x)
        local dh = (f.st==FS_CROUCH or f.st==FS_BLOCK_C) and 22 or 34
        rectb(fs-9,floor(f.y)-dh,18,dh,10)
        if f.atk and f.atk.on then rectb(f.facing==1 and (fs+4) or (fs-4-f.atk.reach),floor(f.y)+f.atk.hy,f.atk.reach,f.atk.hh,7) end
      end
    end
  end
  if P1.combo_show_t>0 and P1.combo_cnt>=2 then out_rect(22,30,36,8,7); print(P1.combo_cnt.." HIT!",24,32,9,true,1,true) end
  if P2.combo_show_t>0 and P2.combo_cnt>=2 then out_rect(182,30,36,8,7); print(P2.combo_cnt.." HIT!",184,32,9,true,1,true) end
  if is_attract and t%30<20 then rect(42,124,116,9,0); print("DEMO PLAY - PRESS ANY BUTTON",44,126,9,true,1,true) end
end

local MODES = {"1P ARCADE","2P VERSUS","TRAINING","CAR BONUS","MOVE LIST"}
local function draw_title()
  if title_idle < 115 then
    if title_idle < 48 then -- Phase 1: Street Crowd Brawl
      cls(13); dither_seam(24,15); rect(0,62,240,74,0)
      out_rect(48,8,144,72,3)
      for wy=14,66,14 do for wx=58,170,18 do rect(wx,wy,10,8,((wx+wy)%4==0) and 9 or 14) end end
      rect(0,80,240,42,6); rect(0,80,240,2,2)
      pal_remap(15,0); spr(202,20,90,0,1,0,0,2,2); spr(204,204,90,0,1,1,0,2,2); pal_reset()
      local p_b1, p_b2 = {4,5,1,13,9,6,14}, {4,5,3,2,7,1,8}
      draw_chibi_spr(2, 92, 114, 1, p_b1, 2, title_idle>=22 and 108 or 96, false, false)
      if title_idle >= 22 then
        pal_remap(15,0); spr(18,120,76,0,2,0)
        if title_idle < 30 then spr(76,114,72,0,1,0,0,2,2); spr(236,122,68,0,1,0,0,2,2) end
        pal_reset()
        local fdt = title_idle - 22
        local kx = min(216, 134 + fdt * 4)
        local ky = 110 - floor(sin(min(1, fdt / 18) * 3.1) * 14)
        draw_chibi_spr(9, kx, ky, -1, p_b2, 2, 172, false, fdt <= 3, true)
      else
        draw_chibi_spr(9, 148, 114, -1, p_b2, 2, 99, false, false)
      end
      rect(0,122,240,14,0); line(0,122,240,122,9)
      print("CAPCOM 1992 // NGPC POCKET TRIBUTE",52,126,9,true,1,true)
    elseif title_idle < 88 then -- Phase 2: Vertical Pan Up Skyscraper
      cls(13); dither_seam(90,15); rect(0,98,240,38,15)
      out_rect(44,0,152,136,15); rect(50,0,140,136,3)
      local pan = (title_idle - 48) * 5
      for row=0,9 do
        local wy = (row * 16 + pan) % 144 - 8
        for col=0,5 do rect(58+col*22, wy, 12, 8, ((row+col)%3==0) and 9 or 14) end
      end
      out_rect(42,54,156,18,0); rectb(42,54,156,18,9)
      print("THE WORLD WARRIORS",66,60,9,true,1,false)
    else -- Phase 3: Rooftop Lightning Flash & Logo Slam
      local fl = (title_idle < 94 and title_idle % 2 == 0) and 1 or 13
      cls(fl); rect(0,62,240,74,0)
      line(180,0,154,24,9); line(154,24,168,28,1); line(168,28,136,62,9)
      local sy = min(4, floor((title_idle - 88) * 0.4))
      out_rect(10,sy,220,38,0); rectb(10,sy,220,38,9); rectb(11,sy+1,218,36,7)
      print("STREET FIGHTER",16,sy+6,7,false,2,false)
      print("STREET FIGHTER",15,sy+4,9,false,2,false)
      out_rect(188,sy+4,28,15,7); rectb(188,sy+4,28,15,9)
      rect(192,sy+6,5,11,9); rect(192,sy+6,5,3,1); rect(201,sy+6,5,11,9); rect(201,sy+6,5,3,1); rect(210,sy+6,3,5,9)
      out_rect(26,sy+21,188,13,7); rectb(26,sy+21,188,13,9)
      print("CHAMPION EDITION // "..(turbo and "HF TURBO" or "CE NORMAL"),62,sy+25,1,true,1,true)
    end
    return
  end
  cls((t%120<3) and 1 or 13); dither_seam(28,15); rect(0,36,240,26,7); dither_seam(34,8); rect(0,62,240,74,0)
  for s=0,7 do rect(s*32,42+(s%3)*5,22,20,15); rect(s*32+4,46+(s%3)*5,4,3,9); rect(s*32+12,48+(s%3)*5,4,3,14) end
  for i=-3,9 do line(120+i*12,62,120+i*28,114,13) end
  line(0,62,240,62,9); line(0,63,240,63,8)
  -- Beveled Arcade SF2' Emblem Box
  out_rect(10,4,220,38,0); rectb(10,4,220,38,9); rectb(11,5,218,36,7)
  print("STREET FIGHTER",16,10,7,false,2,false)
  print("STREET FIGHTER",16,9,8,false,2,false)
  print("STREET FIGHTER",15,8,9,false,2,false)
  -- Pixel-art II' Crest right of SF header
  out_rect(188,8,28,15,7); rectb(188,8,28,15,9)
  rect(192,10,5,11,9); rect(192,10,5,3,1); rect(201,10,5,11,9); rect(201,10,5,3,1); rect(210,10,3,5,9)
  out_rect(26,25,188,13,7); rectb(26,25,188,13,9)
  print("CHAMPION EDITION // "..(turbo and "HF TURBO" or "CE NORMAL"),62,29,1,true,1,true)
  -- Left & Right Live 2x-Scale NGPC Chibi Fighters
  local fire_f = (t%90 >= 58)
  draw_chibi_spr(1, 32, 110, 1, CHARS[1].p1, 2, fire_f and 108 or (t%30<15 and 96 or 99), false, false)
  if fire_f then spr(72, 54, 78, 0, 1, 0, 0, 2, 2) end
  local c_pool = {2, 3, 4, 6, 10, 12}
  local r_cid = c_pool[1 + (floor(t/180) % #c_pool)]
  local r_bid = (r_cid==3 and 163 or (r_cid==6 and 166 or (t%30<15 and 99 or 96)))
  draw_chibi_spr(r_cid, 208, 110, -1, CHARS[r_cid].p1, 2, r_bid, false, false)
  -- Center Mode Select Panel
  out_rect(70,48,100,62,0); rectb(70,48,100,62,9); rectb(71,49,98,60,7)
  for i, m in ipairs(MODES) do
    local y = 52+(i-1)*11
    if i==title_cursor then rect(74,y-1,92,10,13); rectb(74,y-1,92,10,9) end
    print((i==title_cursor and "> " or "  ")..m,86,y+2,i==title_cursor and 9 or 1,true,1,true)
  end
  rect(0,114,240,22,0); line(0,114,240,114,9)
  print("UP/DN:MODE  L/R:SPEED  Z/ENTER:START",46,118,14,true,1,true)
  print("12 FIGHTERS // 1P/2P/TOUCH/GAMEPAD",50,126,2,true,1,true)
end

local function update_title()
  if any_p1_press() then
    title_idle = 115
  else
    title_idle = title_idle + 1
    if title_idle==22 then sfx_play(4,28,12,2)
    elseif title_idle==48 then sfx_play(7,40,22,2)
    elseif title_idle==88 then sfx_play(8,22,18,3) end
    if title_idle>=480 then
      is_attract=true; attract_t=0; game_mode=1; local a=rand(1,12); state=ST_ATTRACT; start_match(a,(a%12)+1,1); return
    end
  end
  if inp[1].p[1] then title_cursor=(title_cursor-2)%#MODES+1; sfx_play(0,56,4) end
  if inp[1].p[2] then title_cursor=title_cursor%#MODES+1; sfx_play(0,56,4) end
  if inp[1].p[3] or inp[1].p[4] then turbo=not turbo; sfx_play(0,62,4) end
  if inp[1].p[5] or inp[1].p[7] or (keyp and (keyp(48) or keyp(50))) then
    sfx_play(1,52,12)
    if title_cursor==5 then prev_state=ST_TITLE; state=ST_GUIDE; guide_page=1
    elseif title_cursor==4 then game_mode=4; p1_pick=1; start_car_bonus()
    else game_mode=title_cursor; p1_ready=false; p2_ready=(game_mode==1); state=ST_SELECT; sync_music(0) end
  elseif inp[1].p[6] then sfx_play(0,52,6); prev_state=ST_TITLE; state=ST_GUIDE; guide_page=1 end
end

local function draw_select()
  cls(13); dither_seam(14,0); rect(0,0,240,14,0); line(0,14,240,14,9)
  print("PLAYER SELECT // "..(turbo and "HYPER" or "CHAMPION"),34,4,9,true,1,true)
  for i=1,12 do
    local x, y, c = 44+((i-1)%4)*38, 19+floor((i-1)/4)*28, CHARS[i]
    out_rect(x,y,34,24,c.p1[3])
    rect(x,y+10,34,7,c.p1[4])
    pal_remap(1, c.p1[4])
    for rx=0,3 do spr(13, x+1+rx*8, y+6, 0) end
    pal_reset()
    draw_chibi_head(i, x+17, y+9, 1, c.p1, 1, false)
    rect(x,y+17,34,7,0); print(c.name,x+2,y+18,1,true,1,true)
    if i==p1_cursor then
      rectb(x-1,y-1,36,26,p1_ready and 10 or 9)
      rect(x,y,10,7,p1_ready and 10 or 9); print("1P",x+1,y+1,0,true,1,true)
    end
    if i==p2_cursor then
      rectb(x,y,34,24,p2_ready and 14 or 7)
      rect(x+24,y,10,7,p2_ready and 14 or 7); print("2P",x+25,y+1,1,true,1,true)
    end
  end
  local c1, c2 = CHARS[p1_cursor], CHARS[p2_cursor]
  local b1 = (p1_cursor==3 and 163 or ((p1_cursor==5 or p1_cursor==6 or p1_cursor==7) and 166 or (t%28<14 and 96 or 99)))
  local b2 = (p2_cursor==3 and 163 or ((p2_cursor==5 or p2_cursor==6 or p2_cursor==7) and 166 or (t%28<14 and 99 or 96)))
  rect(4,86,34,6,0); draw_chibi_spr(p1_cursor, 21, 88, 1, c1.p1, 1, b1, false, false); draw_flag(p1_cursor, 6, 94)
  rect(202,86,34,6,0); draw_chibi_spr(p2_cursor, 219, 88, -1, c2.p1, 1, b2, false, false); draw_flag(p2_cursor, 222, 94)
  out_rect(4,106,112,26,0); rectb(4,106,112,26,9)
  print("1P: "..c1.name.." ("..c1.country..")",8,109,9,true,1,true)
  print(c1.sp[1].." / "..c1.sp[2],8,118,14,true,1,true)
  out_rect(124,106,112,26,0); rectb(124,106,112,26,7)
  print((game_mode==2 and "2P: " or "VS: ")..c2.name.." ("..c2.country..")",128,109,7,true,1,true)
  print(c2.stage,128,118,1,true,1,true)
end

local function update_select()
  if not p1_ready then
    if inp[1].p[3] then p1_cursor=(p1_cursor-2)%12+1; sfx_play(0,58,4) end
    if inp[1].p[4] then p1_cursor=p1_cursor%12+1; sfx_play(0,58,4) end
    if inp[1].p[1] then p1_cursor=(p1_cursor-5)%12+1; sfx_play(0,58,4) end
    if inp[1].p[2] then p1_cursor=(p1_cursor+3)%12+1; sfx_play(0,58,4) end
    if inp[1].p[5] or inp[1].p[7] or (keyp and (keyp(48) or keyp(50))) then
      p1_ready=true; p1_pick=p1_cursor; sfx_play(1,56,10)
      if game_mode==1 then
        arcade_idx=1; arcade_order={}
        for i=1,12 do if i~=p1_pick then table.insert(arcade_order, i) end end
        table.insert(arcade_order, p1_pick); p2_cursor=arcade_order[1]
      end
      return
    end
  end
  if game_mode==2 and not p2_ready then
    if inp[2].p[3] then p2_cursor=(p2_cursor-2)%12+1; sfx_play(0,54,4) end
    if inp[2].p[4] then p2_cursor=p2_cursor%12+1; sfx_play(0,54,4) end
    if inp[2].p[1] then p2_cursor=(p2_cursor-5)%12+1; sfx_play(0,54,4) end
    if inp[2].p[2] then p2_cursor=(p2_cursor+3)%12+1; sfx_play(0,54,4) end
    if inp[2].p[5] or inp[2].p[7] then p2_ready=true; p2_pick=p2_cursor; sfx_play(1,56,10) end
  elseif game_mode==3 and p1_ready and not p2_ready then
    if inp[1].p[3] then p2_cursor=(p2_cursor-2)%12+1; sfx_play(0,54,4) end
    if inp[1].p[4] then p2_cursor=p2_cursor%12+1; sfx_play(0,54,4) end
    if inp[1].p[1] then p2_cursor=(p2_cursor-5)%12+1; sfx_play(0,54,4) end
    if inp[1].p[2] then p2_cursor=(p2_cursor+3)%12+1; sfx_play(0,54,4) end
    if inp[1].p[5] or inp[1].p[7] or (keyp and (keyp(48) or keyp(50))) then p2_pick=p2_cursor; p2_ready=true; sfx_play(1,56,10) end
  end
  if inp[1].p[6] then if p1_ready then p1_ready=false else state=ST_TITLE end; return end
  if p1_ready and p2_ready then p2_pick=p2_cursor; state=ST_VS; freeze_t=90; sfx_play(11,50,14); sync_music(6) end
end

local function draw_vs()
  cls(0); rect(0,22,240,88,13); dither_seam(22,0); dither_seam(102,0)
  for i=0,6 do line(0,30+i*11,240,30+i*11,15) end
  local c1, c2 = CHARS[p1_pick], CHARS[p2_pick]
  local p2pal = (p1_pick==p2_pick) and c2.p2 or c2.p1
  local b1 = (p1_pick==3 and 163 or ((p1_pick==5 or p1_pick==6 or p1_pick==7) and 166 or 96))
  local b2 = (p2_pick==3 and 163 or ((p2_pick==5 or p2_pick==6 or p2_pick==7) and 166 or 96))
  out_rect(14,28,82,76,c1.p1[3]); rectb(14,28,82,76,9)
  draw_chibi_spr(p1_pick, 55, 88, 1, c1.p1, 2, b1, false, false)
  rect(14,90,82,14,0); print(c1.name,20,94,9,false,1,false); draw_flag(p1_pick, 78, 93)
  out_rect(144,28,82,76,p2pal[3]); rectb(144,28,82,76,7)
  draw_chibi_spr(p2_pick, 185, 88, -1, p2pal, 2, b2, false, false)
  rect(144,90,82,14,0); print(c2.name,150,94,9,false,1,false); draw_flag(p2_pick, 208, 93)
  print("VS",110,59,8,false,2,false); print("VS",109,58,9,false,2,false)
  print("STAGE: "..c2.stage,54,118,14,true,1,true)
end

local function update_car_bonus()
  if match_banner_t>0 then match_banner_t=match_banner_t-1 end
  if car.done then
    freeze_t=freeze_t-1
    if freeze_t<=0 then
      if game_mode==1 then state=ST_VS; freeze_t=70; p2_pick=arcade_order[arcade_idx] or 4; sync_music(6)
      else state=ST_TITLE; title_idle=115; sync_music(0) end
    end
    return
  end
  push_input_hist(P1); update_fighter(P1, nil)
  if P1.st==FS_IDLE or P1.st==FS_WALKF or P1.st==FS_WALKB then P1.facing = (P1.x<=car.x) and 1 or -1 end
  if P1.x>car.x-36 and P1.x<car.x+36 and P1.y>=FLOOR_Y-12 then P1.x=(P1.x<car.x) and (car.x-36) or (car.x+36) end
  if P1.atk and P1.atk.on and not P1.atk.hit then
    local hx1 = P1.facing==1 and (P1.x+4) or (P1.x-4-P1.atk.reach)
    local hx2 = P1.facing==1 and (P1.x+4+P1.atk.reach) or (P1.x-4)
    if hx2>=car.x-38 and hx1<=car.x+38 then
      P1.atk.hit=true; car.hp=max(0, car.hp-max(3,floor(P1.atk.dmg*0.5))); car.hit_t=6; p1_score=p1_score+200
      sfx_play(4,30,10,2); add_shake(2,5); spawn_fx("HIT",car.x+(P1.x<car.x and -24 or 24),FLOOR_Y-14,9,10)
    end
  end
  for i=#projs,1,-1 do
    local p = projs[i]; p.x=p.x+p.vx
    if abs(p.x-car.x)<34 then
      car.hp=max(0, car.hp-6); car.hit_t=6; p1_score=p1_score+200; sfx_play(4,34,10,2); spawn_fx("HIT",p.x,p.y,14,10); table.remove(projs,i)
    elseif p.x<-10 or p.x>STG_W+10 then table.remove(projs,i) end
  end
  car.sub=car.sub+1; if car.sub>=60 then car.sub=0; car.time=max(0,car.time-1) end
  if car.hit_t>0 then car.hit_t=car.hit_t-1 end
  if car.hp<=0 or car.time<=0 then
    car.done=true; freeze_t=90
    if car.hp<=0 then p1_score=p1_score+30000; match_banner="PERFECT! +30000"; sfx_play(11,52,20,0) else match_banner="TIME OVER" end
    match_banner_t=90
  end
end

local function draw_car_bonus()
  draw_stage(2, cam_x)
  local sx = floor(car.x-cam_x) + (car.hit_t>0 and (t%2==0 and 2 or -2) or 0)
  local cid_car = (car.hp > 35) and 224 or 230
  pal_remap(15, 0)
  if car.hp <= 70 and car.hp > 35 then pal_remap(12, 13); pal_remap(13, 3) end
  spr(cid_car, sx-48, FLOOR_Y-32, 0, 2, 0, 0, 6, 2)
  pal_reset()
  if car.hp < 50 then
    circ(sx-18+(t%6), FLOOR_Y-32-(t%14), 4, 3); circ(sx+8, FLOOR_Y-36-(t%10), 5, 2)
  end
  if car.hit_t > 0 then
    pal_remap(15, 0)
    spr(76, sx-26, FLOOR_Y-28, 0, 1, 0, 0, 2, 2); spr(236, sx+10, FLOOR_Y-30, 0, 1, 0, 0, 2, 2)
    pal_reset()
  end
  draw_fighter(P1, cam_x)
  for _, p in ipairs(projs) do spr(72, floor(p.x-cam_x)-8, floor(p.y)-8, 0, 1, p.vx<0 and 1 or 0, 0, 2, 2) end
  for _, e in ipairs(fx) do spr(76, floor(e.x-cam_x)-8, floor(e.y)-8, 0, 1, 0, 0, 2, 2) end
  rect(60,4,120,8,7); rectb(59,3,122,10,1)
  if car.hp>0 then rect(60,4,floor(120*car.hp/car.max_hp),8,9) end
  rect(72,14,96,9,0); rectb(72,14,96,9,15); print("SMASH THE CAR! TIME:"..string.format("%02d",car.time),76,16,9,true,1,true)
  if match_banner_t>0 then rect(50,52,140,16,0); rectb(50,52,140,16,9); print(match_banner,70,57,9,true,1,false) end
end

local function draw_guide()
  cls(0); rect(8,6,224,124,13); rectb(8,6,224,124,9)
  print("SF2' CE // COMMAND & MECHANICS",34,10,9,true,1,true)
  if guide_page==1 then
    print("CONTROLS: ARROWS MOVE  Z:LP  X:LK  A:HP  S:HK",16,22,1,true,1,true)
    print("2P KEYS : I/J/K/L MOVE  Y:LP  N:LK  U:HP  H:HK",16,30,14,true,1,true)
    print("GUARD   : HOLD BACK(MID/AIR)  DOWN-BACK(LOW)",16,40,1,true,1,true)
    print("THROW   : CLOSE + F/B+HP/HK OR LP+LK",16,48,1,true,1,true)
    print("CANCEL  : SPECIAL DURING NORMAL HIT/HITSTOP",16,56,9,true,1,true)
    print("DIZZY   : MASH BUTTONS/DIRS TO RECOVER FAST",16,64,1,true,1,true)
    print("COMMAND : F+LP OVERHEAD/LUNGES  CHUN AIR D+LK",16,74,14,true,1,true)
    print("ZONING  : LP/LK SLOW SHOT  HP/HK FAST SHOT",16,82,1,true,1,true)
    print("PAGE 1/3 - L/R:PAGE  X/Z:BACK",56,118,9,true,1,true)
  else
    local s_i = (guide_page==2) and 1 or 7
    for k=0,5 do
      local c, y = CHARS[s_i+k], 22+k*15
      print(c.name,14,y,9,true,1,true)
      print(c.sp[1].."("..c.cmd[1]..") "..c.sp[2].."("..c.cmd[2]..")",52,y,1,true,1,true)
      print(c.sp[3].."("..c.cmd[3]..")",52,y+7,14,true,1,true)
    end
    print("PAGE "..guide_page.."/3 - L/R:PAGE  X/Z:BACK",56,118,9,true,1,true)
  end
end

local function update_guide()
  if inp[1].p[3] then guide_page=(guide_page-2)%3+1; sfx_play(0,56,4) end
  if inp[1].p[4] then guide_page=guide_page%3+1; sfx_play(0,56,4) end
  if inp[1].p[5] or inp[1].p[6] or inp[1].p[7] or (keyp and keyp(48)) then state=prev_state end
end

local function draw_win()
  cls(13); dither_seam(24,0)
  local w = (P1.wins>=P2.wins) and P1 or P2
  local l = (w==P1) and P2 or P1
  out_rect(12,14,216,108,0); rectb(12,14,216,108,9)
  local bid = (w.cid==3 and 195 or 128)
  out_rect(22,24,56,66,w.pal[3]); rectb(22,24,56,66,9)
  draw_chibi_spr(w.cid, 50, 86, 1, w.pal, 2, bid, false, false)
  draw_flag(w.cid, 62, 27)
  out_rect(188,24,32,36,l.pal[3]); rectb(188,24,32,36,7)
  draw_chibi_head(l.cid, 204, 39, -1, l.pal, 1, false, true)
  rect(188,50,32,10,7); print("LOSER",194,52,1,true,1,true)
  print(w.c.name.." WINS!",86,28,9,false,1,false)
  print(string.sub(w.c.quote,1,24),86,44,1,true,1,true)
  print(string.sub(w.c.quote,25,48),86,52,1,true,1,true)
  print(string.format("SCORE: %06d",p1_score),86,74,14,true,1,true)
  print("Z/LP:NEXT  X/LK:TITLE",66,108,9,true,1,true)
end

local function step_fight()
  if round_over_t>0 then
    round_over_t=round_over_t-1
    if match_banner_t>0 then match_banner_t=match_banner_t-1 end
    if ko_echo_t>0 then
      ko_echo_t=ko_echo_t-1
      if ko_echo_t==24 or ko_echo_t==12 then sfx_play(8,20,14,3,ko_echo_t==24 and 8 or 4) end
    end
    if round_over_t%2==0 then
      if P1.st==FS_KD then update_fighter(P1,P2) end
      if P2.st==FS_KD then update_fighter(P2,P1) end
    end
    if round_over_t==62 then
      sfx_play(1,52,16,0); sfx_play(11,57,22,2)
      local wf = (P1.hp>=P2.hp) and P1 or P2
      if wf.hp>0 then wf.st=FS_WIN; wf.st_t=0 end
    end
    if round_over_t<=56 and round_over_t>=10 and game_mode==1 and P1.hp>=P2.hp and round_over_t%4==0 then
      sfx_play(0,64,2,3,6)
    end
    if round_over_t==0 then
      if is_attract then attract_t=9999
      elseif P1.wins>=2 or P2.wins>=2 then state=ST_WIN; sync_music(7)
      else round_num=round_num+1; start_round() end
    end
    return
  end
  if freeze_t>0 then
    freeze_t=freeze_t-1
    if freeze_t==24 then match_banner="FIGHT!"; sfx_play(1,56,14,0); sfx_play(7,52,10,3) end
    if match_banner_t>0 then match_banner_t=match_banner_t-1 end
    return
  end
  if hitstop>0 then
    if P1.is_cpu then run_ai(P1,P2) else push_input_hist(P1) end
    if P2.is_cpu then run_ai(P2,P1) else push_input_hist(P2) end
    local b1 = get_atk_trigger(P1, true); if b1>0 then P1.buf_btn=b1; P1.buf_btn_t=6; if P1.st==FS_ATTACK and P1.atk and not P1.atk.sp then check_special_cmd(P1, b1, false) end end
    local b2 = get_atk_trigger(P2, true); if b2>0 then P2.buf_btn=b2; P2.buf_btn_t=6; if P2.st==FS_ATTACK and P2.atk and not P2.atk.sp then check_special_cmd(P2, b2, false) end end
    hitstop=hitstop-1; return
  end
  if P1.is_cpu then run_ai(P1,P2) end; push_input_hist(P1)
  if P2.is_cpu then run_ai(P2,P1) end; push_input_hist(P2)
  update_fighter(P1,P2); update_fighter(P2,P1); resolve_collisions(P1,P2)
  local target_cam = max(0, min(STG_W-240, (P1.x+P2.x)*0.5-120))
  cam_x = cam_x + (target_cam - cam_x)*0.25
  if game_mode~=3 then
    timer_sub=timer_sub+1; if timer_sub>=60 then timer_sub=0; if timer_sec>0 then timer_sec=timer_sec-1 end end
  else
    if P2.st==FS_IDLE and P2.hp<P2.max_hp then P2.hp=min(P2.max_hp,P2.hp+1) end
    if P1.st==FS_IDLE and P1.hp<P1.max_hp then P1.hp=min(P1.max_hp,P1.hp+1) end
  end
  if (P1.hp>0 and P2.hp>0) and (P1.hp<=25 or P2.hp<=25) and cur_track>=1 and cur_track<=4 then sync_music(5) end
  if (P1.hp<=0 or P2.hp<=0 or timer_sec<=0) and game_mode~=3 then
    if cur_track~=-1 then music(-1); cur_track=-1 end
    sfx_play(8,22,22,0); sfx_play(9,34,18,3); ko_echo_t=36
    if P1.hp<=0 and P2.hp<=0 then match_banner="DOUBLE KO!"
    elseif P1.hp<=0 then P2.wins=P2.wins+1; match_banner=P2.c.name.." WINS"
    elseif P2.hp<=0 then
      P1.wins=P1.wins+1; match_banner=(P1.hp==P1.max_hp) and "PERFECT!" or "K.O.!"
      p1_score=p1_score+2000+timer_sec*100+max(0,P1.hp)*20
    else if P1.hp>=P2.hp then P1.wins=P1.wins+1 else P2.wins=P2.wins+1 end; match_banner="TIME OVER" end
    match_banner_t=90; round_over_t=90
  end
end

local function draw_fight()
  local sx_off = shake_t>0 and rand(-shake_amp,shake_amp) or 0
  local sy_off = shake_t>0 and rand(-shake_amp,shake_amp) or 0
  draw_stage(cur_stage, cam_x+sx_off); draw_fighter(P2, cam_x+sx_off); draw_fighter(P1, cam_x+sx_off)
  for _, p in ipairs(projs) do
    local pid = (p.kind=="BOOM" and 74 or (p.kind=="YOGA" and 206 or 72))
    pal_remap(12,p.col1); pal_remap(14,p.col2)
    spr(pid, floor(p.x-cam_x)-8, floor(p.y)-8+sy_off, 0, 1, p.vx<0 and 1 or 0, 0, 2, 2)
    pal_reset()
  end
  for _, e in ipairs(fx) do
    local ex, ey = floor(e.x-cam_x)-8, floor(e.y)-8
    if e.kind=="BLOCK" then spr(6,ex+4,ey+4,0)
    elseif e.kind=="HIT" then spr(76,ex,ey,0,1,0,0,2,2)
    elseif e.kind=="CRATE" then pal_remap(15,0); spr(78,ex,ey-(e.max-e.life),0,1,0,0,2,2); pal_reset()
    else circ(ex+8,ey+8,max(1,floor(e.life/3)),e.col) end
  end
  for _, pp in ipairs(popups) do
    local px, py, pw = max(4,min(170,floor(pp.x-cam_x)-#pp.text*2)), max(20,floor(pp.y)), #pp.text*4+4
    rect(px-2,py-1,pw,7,0); print(pp.text,px,py,pp.col,true,1,true)
  end
  draw_fight_hud()
  if match_banner_t>0 then
    local bw = #match_banner*6+16; local bx = floor((240-bw)/2)
    rect(bx,54,bw,16,0); rectb(bx,54,bw,16,9); print(match_banner,bx+8,59,9,false,1,false)
  end
  if round_over_t>0 and round_over_t<60 and game_mode==1 and P1.hp>=P2.hp then
    rect(48,74,144,18,0); rectb(48,74,144,18,14)
    print(string.format("TIME %04d  VITAL %04d",timer_sec*100,max(0,P1.hp)*20),78,77,1,true,1,true)
    print("BONUS +"..tostring(2000+timer_sec*100+max(0,P1.hp)*20),96,84,9,true,1,true)
  end
end

function BOOT() sync_music(0) end

function TIC()
  t = t + 1
  for s=1,2 do for b=1,8 do prev_hold[s][b] = inp[s].hold[b] end end
  read_all_inputs()
  if keyp and keyp(13) then sfx_muted = not sfx_muted; sync_music() end
  if keyp and keyp(49) and game_mode==3 then show_hitboxes = not show_hitboxes end
  if keyp and keyp(18) and state==ST_FIGHT and game_mode==3 then trn_guard = trn_guard%3+1 end
  if not paused then
    if shake_t>0 then shake_t=shake_t-1; if shake_t==0 then shake_amp=0 end end
    for i=#fx,1,-1 do fx[i].life=fx[i].life-1; if fx[i].life<=0 then table.remove(fx,i) end end
    for i=#popups,1,-1 do popups[i].y=popups[i].y-0.3; popups[i].life=popups[i].life-1; if popups[i].life<=0 then table.remove(popups,i) end end
  end
  if state==ST_TITLE then update_title(); draw_title()
  elseif state==ST_SELECT then update_select(); draw_select()
  elseif state==ST_VS then draw_vs(); freeze_t=freeze_t-1; if freeze_t<=0 or any_p1_press() then state=ST_FIGHT; start_match(p1_pick,p2_pick,game_mode) end
  elseif state==ST_ATTRACT then
    local hb = human_any_btn()
    if hb or attract_t>=600 then is_attract=false; state=ST_TITLE; title_idle=hb and 115 or 0; sync_music(0); draw_title(); return end
    attract_t=attract_t+1; step_fight(); draw_fight()
  elseif state==ST_FIGHT then
    if keyp and (keyp(48) or keyp(50) or keyp(16)) then paused=not paused; sync_music() end
    if paused then
      draw_fight(); rect(44,34,152,68,0); rectb(44,34,152,68,9)
      print("PAUSED // SF2' CE",76,42,9,true,1,true)
      print("SPACE/ENTER: RESUME",64,56,1,true,1,true)
      print("X/LK: MOVE LIST",64,66,14,true,1,true)
      print("S/HK: EXIT TO TITLE",64,76,7,true,1,true)
      if inp[1].p[6] then paused=false; prev_state=ST_FIGHT; state=ST_GUIDE; guide_page=1 end
      if inp[1].p[8] then paused=false; state=ST_TITLE; title_idle=115; sync_music(0) end
    else
      local steps=1
      if round_over_t==0 and turbo then turbo_acc=turbo_acc+0.25; if turbo_acc>=1 then turbo_acc=turbo_acc-1; steps=2 end end
      for _=1,steps do step_fight() end
      draw_fight()
    end
  elseif state==ST_BONUS then update_car_bonus(); draw_car_bonus()
  elseif state==ST_WIN then
    draw_win()
    if inp[1].p[5] or inp[1].p[7] or (keyp and (keyp(48) or keyp(50))) then
      sfx_play(1,56,8)
      if game_mode==1 and P1.wins>=2 then
        arcade_idx=arcade_idx+1
        if arcade_idx==4 then start_car_bonus()
        elseif arcade_idx<=#arcade_order then p2_pick=arcade_order[arcade_idx]; state=ST_VS; freeze_t=90; sync_music(6)
        else if p1_score>pmem(0) then pmem(0,p1_score) end; state=ST_TITLE; title_idle=115; sync_music(0) end
      else state=ST_TITLE; title_idle=115; sync_music(0) end
    elseif inp[1].p[6] then state=ST_TITLE; title_idle=115; sync_music(0) end
  elseif state==ST_GUIDE then update_guide(); draw_guide() end
end

-- <TILES>
-- 001:000cc00000ceec000ce11ec0ce1111ecce1111ec0ce11ec000ceec00000cc000
-- 002:00c00c00c0ceec0c0ce11ec0cce11ecc0ce11ec0c0ceec0c00c00c0000000000
-- 003:00ee11000e1111e0e119911ee199991ee119911e0e1111e000ee110000000000
-- 004:0e111100e19991e01991191e1991191ee19991e00e1111000000000000000000
-- 005:9001100909088090009119001811118118111181009119000908809090011009
-- 006:00eeee000ec11ce0ec1001cee100001ee100001eec1001ce0ec11ce000eeee00
-- 007:0009000000090000999199900911190000919000090009009000009000000000
-- 008:0009900000911980991119000999900000909000000000000000000000000000
-- 009:0009900000911900991111990919919000999900099009909000000900000000
-- 010:0087700008919800891119707919987008988700007770000000000000000000
-- 011:00ffff000f3223f0f321123ff21ff12ff21ff12ff321123f0f3223f000ffff00
-- 012:f666666f6555556665855856f333333f655885566585585666555556f666666f
-- 013:1010101001010101101010100101010110101010010101011010101001010101
-- 014:f33ff33f322ff223333ff333ffffffff3ff33ff32ff22ff23ff33ff3ffffffff
-- 015:2222f2225555f5555333f333fffffffff2222f22f5555f55f3333f33ffffffff
-- 016:00f717f00f71417ff741741ff477174f0f7474f000ffff000000000000000000
-- 017:00011000001cc10001ccdd101ccdddd1ccdddddc000000000000000000000000
-- 018:000ff11000f991ef11f911efff9911efff9911ef11f911ef00f991ef000ff110
-- 019:00ff1100000f1ef00000f1ef0000f11f0000f11f0000f1ef000f1ef000ff1100
-- 020:00f909f00f91f19ff91111190f11911f0f11911ff91111190f91f19f00f909f0
-- 021:0000000000000000ffffffff4454454455455455ffffffff0000000000000000
-- 022:00ffff000f7744f0f774445ff774455ff774455ff774445f0f7744f000ffff00
-- 023:ff11110000ffff1eff11111000ffff1eff11111000ffff1e0000000000000000
-- 032:0000ff0f00ff66f60f666666f7f7777777ff7777f70f444f00f4ff1f00f411f4
-- 033:0fff0000f666ff0066666ff0777777f077777ff0f4fff4f04f1ff4f044f1f4f0
-- 034:0ffffffff666f666f6696666f6666666f66ff6660f6f444f0f6f4ff10f5f411f
-- 035:fffff000f6666ff0669666ff6666666fff66fff0f4fff4f0f4f1ff4f444f1f4f
-- 036:00000ffff11ff666191f6666111f66fff19f6f440f9f4f1f0f6f4f1100ff41f1
-- 037:fff00000666ff11f6666f19166ff6f114444ff1ff4ff1f4ff4f11f4ff441ff4f
-- 038:f9999999f9899999f99899990f9889990f88ff8800ff444f00f4ff1f00f411f4
-- 039:9999999f9999998f9999989f999989f088ff8f00f4fff4f04f1ff4f044f1f4f0
-- 040:0ff6f66ff6666666f66866fff66f4444f6ff4ff9f6f441f1f6f441110ff54444
-- 041:f66f6f00666666f0666666ffff4fff4ff4f9ff4ff4f1f14f4441114fff4445f0
-- 042:000000ff0000ffdd00ffddff0fdddfff0fdf111f0f17ff1f0f711ff10f171111
-- 043:ff000000ddff0000ffddff00fffdddf0f111fdf011f171f011ff17f0111171f0
-- 044:000000ff00000f66000ff66600f54fff0f54ff1f0f5411f40f5444440f6f6444
-- 045:ff00000066f00000666ff000fff45f004f1ff4f044f1f4f0544445f04446f6f0
-- 046:00000fff000ff44400f5411700f5444700f54ff400f4111400f5411400f54444
-- 047:fff00000444ff00071144f0074444f004ffff4f044111f0054114f0044444f00
-- 048:00f41f1400f5444400f5444400f544ff000f54440000ff5400000f54000000ff
-- 049:441f14f0454445f045544f00f4445f004445f00044ff000045f00000ff000000
-- 050:00ff41f100f5444400f5444400f54f11000f54440000ff5400000f54000000ff
-- 051:4441f14f454445f0444445f01f444f004444f00044ff000045f00000ff000000
-- 052:00f5411100f54744000f4444000f544f0000f54400000ff4000000ff00000000
-- 053:44411f4f454474f044444f00f444f000444f00004ff00000ff00000000000000
-- 054:00f5444400f5444400f544ff00f55444000ff5440000ff5400000fff00000000
-- 055:454445f044444f00f444f0004445f000445ff00044ff0000fff0000000000000
-- 056:00f5444400f51fff00f54144000ff4440000f54400000f54000000ff00000000
-- 057:44444f00ff1fff0041445f00444ff000445f000045f00000ff00000000000000
-- 058:0f1171110f11114400f144ff00f44444000f54440000ff54000000ff00000000
-- 059:111711f0441111f0ff441f0044444f004445f00045ff0000ff00000000000000
-- 060:0f666f110f666fff00f6666600f66666000f66660000ff66000000ff00000000
-- 061:11f666f0fff666f066666f0066666f006666f00066ff0000ff00000000000000
-- 062:000f544f000f54440000ff5400ff1f1f0f11f1f100ff0ff00000000000000000
-- 063:f445f0004445f00045ff0000f1f1ff001f1f11f00ff0ff000000000000000000
-- 064:000fffff00ffffff00ffffff00f4544400f4ff1f0f9f411f0f4f454400f4444f
-- 065:ffff0000fffff000fffff00044445f004f1ff4f044f1f4f044444f00ff444f00
-- 066:0000ffff00ff99990f998111f98f1111f98f1181f9f1f1fff9f11ff1f9f11111
-- 067:ffff00009999ff00111899f01111f89f1811f89f1ff11f9f1ff11f9f11111f9f
-- 068:00000fff000ff44400f5444400f5ff4400ffdfd400f4ffff00f41ff100f54ff4
-- 069:fff00000444ff00044444f004f444f004ffff4f04f1ff4f0ff1f4f0044444f00
-- 070:000fffff00f222290f222991f33222990fffffff000ffddd00f5f11f00f5411f
-- 071:ffffff00922222f0992222f0922223f0ffffffffddddffff4f11f4f04f114f00
-- 072:000000cc0000ccce00ccceee0cceeeeeccceee11ceeee111ceee1111cee11111
-- 073:ccc00000eeccc000eee1cc0011111ec0111111cc1111111e1111111e1111111e
-- 074:0000eeee00eee1110ee11999e1199911e19911000e99100000e9100000e91000
-- 075:1100000011ee00009111e00099911e0011991e0001991e0001991e0001991e00
-- 076:9000001009000018009001110009119900011911111191110881911108819111
-- 077:0100000981000090111009009911900011911000111911111119188011191880
-- 078:00ffffff0f668666f6866666fffffffff3333333f668666ff66666f6f6666666
-- 079:ffffff00668666f06666686fffffffff3333333ff666866f6f66666f6666666f
-- 080:00f4444400f544ff000f54440000ff5400000f54000000ff0000000000000000
-- 081:44444f00f4445f004445f00044ff000045f00000ff0000000000000000000000
-- 082:f9f1e11ff98f1e110f9ff1110f98ff110f988fff0f98f00000ff000000000000
-- 083:f11e1f9f11e1f89f111ff9f011ff89f0fff889f0000f89f00000ff0000000000
-- 084:00f5444f000f5411000f54440000ff5400000f54000000ff0000000000000000
-- 085:ff445f001145f0004445f00045ff000045f00000ff0000000000000000000000
-- 086:00f5444400f54f11000f54ff0000ff5400000f54000000ff0000000000000000
-- 087:44444f00111f4f00ff45f00045ff000045f00000ff0000000000000000000000
-- 088:cee11111ceee1111ceeee111ccceee110cceeeee00ccceee0000ccce000000cc
-- 089:1111111e1111111e1111111e111111cc11111ec0eee1cc00eeccc000ccc00000
-- 090:00e910000e991000e1991100e11999110ee1199900eee1110000eeee00000000
-- 091:01991e0001991e0011991e0099911e009111e00011ee00001100000000000000
-- 092:1111911100011911000911990090011109000018900000100000000000000000
-- 093:1119111111911000991190001110090081000090010000090000000000000000
-- 094:f6686666f66666f6f666666ff3333333ffffffff0f66686600ffffff00000000
-- 095:6666866f6f66666ff666666f3333333fffffffff668666f0ffffff0000000000
-- 096:0000000f000000f200000f22000ff22200f44f320f444f320f77ff3300fff0ff
-- 097:f44444ff2f444f2222f4f222222f222f222222ff22222f2232222f22ffffff00
-- 098:00000000f00000002ff0000077f00000774f0000f44f0000fff0000000000000
-- 099:000000000000000f000000f20000ff22000f44f300f444f300f77ff3000fff0f
-- 100:fffffffff44444ff2f444f2222f4f22f222f222f222222f2332222f2fffffff0
-- 101:0000000000000000ff00000077f00000f74f00002f4f00002ff0000000000000
-- 102:0000000f000000f200000f220000f222000f322200f44f3300f7f0f7000f0f22
-- 103:f44444ff2f444f2222f4f222222f22f722222ff422222f227777ff0027f722f0
-- 104:00000000f00000002f0000007ff000004f000000f00000000000000000000000
-- 105:0000000000000000000000000000000f00000ff20000f222000f322200f44f33
-- 106:000000000000000000000000f44444ff2f444f2222f4f222222f22f722222ff7
-- 107:00000000000000000000000000000000f0000000ff00000074f000007f000000
-- 108:000000ff00000f220000f222000f322200f44f3300f7ff33000ff0ff00000f77
-- 109:44444ff0f444f22f2f4f222222f2222222222222322222ffffffff0077f77f00
-- 110:00000000f00000002fffffff2f44777f2f44777fffffffff0000000000000000
-- 112:00000f7700000f220000f322000f322200f3222f00f444f00f4455f00ffffff0
-- 113:77f777f027f7222f2f0f2222f000f22200000f22000000f40000000f0000000f
-- 114:0000000000000000f00000002f00000032f0000044f00000445f0000ffff0000
-- 115:00000f7700000f220000f322000f322200f3222f00f444f00f4455f00ffffff0
-- 116:77f777f027f7222f2f0f2222f000f22200000f22000000f40000000f0000000f
-- 117:0000000000000000f00000002f00000032f0000044f00000445f0000ffff0000
-- 118:00000f32000000f30000000f000000f200000f220000f44f000f445f000ffff0
-- 119:2222222f222f222222f0f2222f000f22f00000f2000000f4000000f4000000ff
-- 120:00000000f0000000f0000000f00000002f00000044f0000045f00000fff00000
-- 121:00f7ff770000f222000f322200f3222f00f322f00f444f000f455f000fffff00
-- 122:77777f0f27f2222ff00f22220000f22200000f22000000f4000000f4000000ff
-- 123:f000000000000000f00000002f0000003f00000044f0000045f00000fff00000
-- 124:0000f322000f322200f3222f0f3222f00f322f00f444f000f455f000fffff000
-- 125:27f222f0f00f222f0000f22200000f22000000f20000000f0000000f0000000f
-- 126:0000000000000000f00000002f00000022f00000444f0000445f0000ffff0000
-- 128:0000000000000000000000000000000f000000f200000f320000f44f0000f7ff
-- 129:00000f7700000f740000f224f444f2242f44222f222222f032222f007777f000
-- 130:7f0000004f0000004f000000f000000000000000000000000000000000000000
-- 131:00000ff40000f22f000f322200f44f3200f7ff33000ff0f700000f320000f322
-- 132:444ff00044f22f0022222f0022222f002222ffff777f2222222222222222ffff
-- 133:000000000000000000f444f0ff22244f2222445f222ffff0fff0000000000000
-- 134:00000000000000000000000000000000000000ff00000f220000f322000f4f33
-- 135:00000000000000000000000000000000444ff000f4f22f0022222f0022222f00
-- 137:0000000f000000f200000f220000f44f0000f7ff00000ff0000000f300000f32
-- 138:f4444ff02f44f22f2222222f322222f7332222f4f77777f02227f222222f0f22
-- 139:0000000000000000000000007f0000004f00000000000000fff00000222ff000
-- 140:000000000000000f000000f200000f3200000f33000000f30000000f000000f3
-- 141:fffffffff444ff7722f44f74222f44442222f77432222f7777777fff2227f22f
-- 142:00000000f0000000f0000000f0000000f0000000f00000000000000000000000
-- 144:000000f300000f320000f3220000f2220000f22f000f44f0000f45f0000ffff0
-- 145:22222ff022f2222f2f00f222f000f44400000fff000000000000000000000000
-- 146:0000000000000000f0000000f000000000000000000000000000000000000000
-- 147:0000f322000f3222000f222f000f22f000f222f000f444f000f445f000fffff0
-- 148:2fff0000f0000000000000000000000000000000000000000000000000000000
-- 150:000ff0f700000f320000f322000f322200f444ff00f455f000fffff000000000
-- 151:7777f00022222fff22222222f22222220fffffff000000000000000000000000
-- 152:00000000f00000002ffff4f02222445fffffffff000000000000000000000000
-- 153:0000f322000f444f000f455f000ffff000000000000000000000000000000000
-- 154:2f0000f20000000f000000000000000000000000000000000000000000000000
-- 155:22244f00f4445f000ffff0000000000000000000000000000000000000000000
-- 156:00000f320000f322000f3222000f222f00f444f000f455f000fffff000000000
-- 157:22f0f2222f000f22f00000f2000000f2000000f4000000f4000000ff00000000
-- 158:f00000002f00000022f0000022f0000044f0000045f00000fff0000000000000
-- 160:000000000000ff44000f22f40f4f3222f74ff3320fff0f7700000f3200000f32
-- 161:0000000044ff00004f22ff00222222f422222f227777ff0f2227f00022f22f00
-- 162:0000000000000000000000004f00000077f00000ff0000000000000000000000
-- 163:0000000f000000f200000f22000ff4f200f464f300f66ff3000ff0f700000f72
-- 164:f44444ff2f444f22274447222277722f2227222f3227222f7222227f227f7227
-- 165:00000000f00000002ff00000664f0000f64f0000f0f0000000000000f0000000
-- 166:000000ff0000ff4400ff44450f444444f4474f45f4444f440ffff0f700000f22
-- 167:ffffffff44444444444ff4454444444444444445544444547777777722299222
-- 168:ff0000004ff00000444ff000444f77f04f4ff74f4f44fff07f00000022f00000
-- 169:00000000fffffffff7444222ffffffff00000000000000000000000f000000f3
-- 170:ffffffff222222222222222233222222f777777ff222722f322f0f2222f000f2
-- 171:00000000ffffffff2224447f3fffffff00000000000000002f00000022f00000
-- 172:000000000000000000000000000000000000000000000000000000000000ffff
-- 173:00000000000000000000000000000000000000000000000000000000f0000000
-- 176:0000f322000f322200f3222f00f222f00f444f000f455f000fffff0000000000
-- 177:2f0f22f0f000f22f0000f22200000f2200000f4400000f4400000fff00000000
-- 178:0000000000000000f0000000f00000004f0000005f000000ff00000000000000
-- 179:0000f22f000f22f00000ff0f000000f100000f110000f122000f1111000fffff
-- 180:744f4472f44f44f244f0f44f1f000f111f000f111f000f121f000f11ff000fff
-- 181:f0000000f000000000000000f00000001f00000021f00000111f0000ffff0000
-- 182:0000f322000f322200f5444400f5444f0f6666f0f66666f0f66666f0fffffff0
-- 183:22f22f222f0000f2f000000f0000000000000000000000000000000000000000
-- 184:222f00002222f00044445f00f4445f000f6666f00f66666f0f66666f0fffffff
-- 185:00000f3200000f440000f4550000ffff00000000000000000000000000000000
-- 186:2f00000ff0000000f0000000f000000000000000000000000000000000000000
-- 187:222f0000f444f000f445f000fffff00000000000000000000000000000000000
-- 188:000f22220ff44f22f544f322f554f3320ffff33300000fff0000000000000000
-- 189:2fffffff27222222272222222732222f2233222fffffffff0000000000000000
-- 190:ff0000002fff00002222ff00fff444f000f455f000fffff00000000000000000
-- 192:00000000000000ee00000e110000e1ff000e1f44000e1f64000e1f660000e1ff
-- 193:eeeeeeee11111111ffffffff444466662222226622777722222332222233322f
-- 194:00000000ee000000ffe000004ff10000444f1000464f1000666f1000f4f10000
-- 195:0000000f000000f200000f320000f44f0000f6ff0000000f000000f200000f22
-- 196:f4444ff02744722f2277222f322222ff722222227222222222227fff22fff000
-- 197:000000000000000000f111f00f11121fff44111f444ffff0ff00000000000000
-- 198:00000fff0000f444000f444500f4444400f74f4400fff0f700000f220000f322
-- 199:ffffffff44444444444ff4444444444454444444777777772229922222f0f222
-- 200:00000000fffffffff447777ff447777ffffffffff0000000f00000002f000000
-- 202:00000fff0000f666000f6444000f4f44000f44440000ff440ff0fcc1f44ffccc
-- 203:fff00000666f00004446f0004f44f0004444f00044ff00001ccf0ff0cccff44f
-- 204:00000fff0000f7770000f7770000f4f40000f44400000ff400f4f7710f44f777
-- 205:fff00000777fff00ffffff004f44f0004444f00044ff0000177f4f00777f44f0
-- 206:0000007700077889007889910789911178911111789111110799111100789111
-- 207:8000000087000000987000009987000019987000119870001198700019870000
-- 208:00000e11000000ee000000000000000000000000000000000000000000000000
-- 209:ffffffff11111111eeeeeeee0000000000000000000000000000000000000000
-- 210:ffe00000ee000000000000000000000000000000000000000000000000000000
-- 211:0000f444000f444f00f111f000f111f00f1221f00f1111f00ffffff000000000
-- 212:ff00000000000000000000000000000000000000000000000000000000000000
-- 214:000f544400f5444f0f6666f0f66666f0fffffff0000000000000000000000000
-- 215:4f000f44000000f40000000f0000000f0000000f000000000000000000000000
-- 216:45f00000445f00006666f00066666f00ffffff00000000000000000000000000
-- 218:0ff4fccc0000fccc0000fddd0000f3330000f33f000f666f000fffff00000000
-- 219:cccf4ff0cccf0000dddff000f333f0000f33f0000f666f000fffff0000000000
-- 220:00ff0f7700000f7700000fdd0000fddd0000f33f000f111f000fffff00000000
-- 221:77f0ff0077f00000dfddf000dfddf0000f33f0000f111f000fffff0000000000
-- 222:0007899900788998078988707887700000000000000000000000000000000000
-- 223:9870000077000000000000000000000000000000000000000000000000000000
-- 224:0000000000000000000000000000000000000000000fffff0fc11111f1cc99cc
-- 225:000000000000000f000000f100000fce0000fceeffffffffcccccccccccccccc
-- 226:ffffffff11111ccccee1f1eeee11fe1eeeeefeeeffffffffccccccccccccfccc
-- 227:ffffffffccccccccee1fcccce11fcccdeeeffcccffffffffcccccccccccccccc
-- 228:ffffff00c11111f0cce1ccf0dcc1ccf0cccccccfffffffffcccccccccccfcccc
-- 229:0000000000000000000000000000000000000000ffffff00cccc88f0ccccc87f
-- 230:0000000000000000000000000000000000000000000000ff000ff33d00f383dd
-- 231:0000000000000000000000000000000000000000ffff000fd333ffffdddddd33
-- 232:000000000000000000ffff000f3dd3fff3feef3ffddddddf33dddd3ff00dd333
-- 233:000000000000000000fffff0ffc113df0f1e3ddf0f3ddddff3ddd333ddd3300f
-- 234:0000000000000000000000000000000000000000f00000ffffffff33dd33333d
-- 235:0000000000000000000000000000000000000000ffff0000ddd3ff00ddd37f00
-- 236:000008890008899100899111089111ff08911f328911f2218911f2118911f321
-- 237:988000001998800011199800ff11198023f11980122f1198112f1198123f1198
-- 238:000000ff00000f880000f899000f891100f899110f8991110f891111f8991199
-- 239:00000000f00000008f00f00098ff8f00998898f01998998f1199198f1111198f
-- 240:fcddddddfcccccccf99fddddfddddff30fffff3200000f21000000f30000000f
-- 241:ddddddddccccccccfffffddd322233ff1111123ffffff12f222223f0ffffff00
-- 242:ddddfdddccccccccddddffffddddddddffffffff000000000000000000000000
-- 243:ddddddddccccccccdddddddddddddddfffffffff0000000f0000000000000000
-- 244:dddfddddccccccccfffddddff33222333211111221fffff1f322222300ffffff
-- 245:dddddddfcccccccffddddf9fffdddddf3ffffff02f000000f0000000f0000000
-- 246:0f33ddddf333f33ffdddff3f0ffff3f100000f2f000000ff0000000000000000
-- 247:00dddd33fff33333223ffddd1f23fffff32f0000fff000000000000000000000
-- 248:3f3dddd333333333ddddddddffffffff00000000000000000000000000000000
-- 249:f0fdddd333333333ddddddddffffffff00000000000000000000000000000000
-- 250:33dd00dd333ffff3ddff3f22fff3f11f000f2ff30000ffff0000000000000000
-- 251:ddddddf033f333f03ffdddf023ffff002f000000f00000000000000000000000
-- 252:08911f33089911ff008991110008899100000889000000000000000000000000
-- 253:33f11980ff119980111998001998800098800000000000000000000000000000
-- 254:f8911988f89119880f8911990f89911100f89911000f88990000ff88000000ff
-- 255:9111998f991198f091198f001198f000198f000088f00000ff00000000000000
-- </TILES>

-- <WAVES>
-- 001:0000000000000000ffffffffffffffff
-- 002:0123456789abcdeffedcba9876543210
-- 003:00112233445566778899aabbccddeeff
-- 004:ffffffff000000000000000000000000
-- 005:ffdc98cdfea74200ffdc98cdfea74200
-- </WAVES>

-- <SFX>
-- 000:24025400a20ef100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100404000000000
-- 001:1400147231c472c4c2c4f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100409000000000
-- 002:40036001900ec00cf100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100b00000000000
-- 003:0001130e500ba109f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100b00000000000
-- 004:0000030d100c330a60099308c008f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100a14000000000
-- 005:1404317272c0b20ef100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100402000000000
-- 006:00021401245f417e630c930ac009f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100b07000000000
-- 007:040e0441137321c544c671c7b2c7f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100b09000000000
-- 008:0000030d100c230b300a500973089008b008d008f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100a20000000000
-- 009:030f100d330b50099308f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100a17000000000
-- 010:32024444627284c5b273f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100407000000000
-- 011:04000440147021c051c092c0c2c0f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100410000000000
-- 012:3400340044004100510051015100610f630063016300730f730073017300830f830083018300830f9300a300b200c200d200e200f100f100f100f100310000000000
-- 013:230033004300550065007500850095009500a500a500b500c200d200f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100110000000000
-- 014:550055006500750075008500820092009200a200a200b200b200b200c200c200c200d200d200e200f100f100f100f100f100f100f100f100f100f100310000000000
-- 015:25044501600e800ba009c008f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100a00000000000
-- 016:24003400530063008300a300c300e300f300f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100300000000000
-- 017:60028000a00ec00cd00af100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100f100500000000000
-- </SFX>

-- <PATTERNS>
-- 000:600009000000000000000000000000000000600009000000000000000000000000000000d000c8000000000000000000000000000000000000000000000000000000100000000000b00009000000000000000000900009000000000000000000800009000000000000000000900009000000000000000000b000c8000000000000000000000000000000000000000000d000c8000000000000000000000000000000000000000000000000000000100000000000b00009000000d00009000000
-- 001:d00007000000000000000000000000000000d000070000000000000000000000000000008000e80000000000000000000000000000000000000000000000000000000000000000006000e80000000000000000004000e8000000000000000000f000e60000000000000000004000e80000000000000000006000e80000000000000000000000000000000000000000008000e80000000000000000000000000000000000000000000000000000000000000000006000e8000000000000000000
-- 002:6000d20000006000d40000006000d20000006000d40000006000d20000006000d40000006000d20000006000d4000000e000d2000000e000d4000000e000d2000000e000d40000004000d20000004000d40000004000d20000004000d40000006000d20000006000d40000006000d20000006000d40000009000d20000009000d4000000b000d2000000b000d4000000d000d2000000d000d4000000d000d2000000d000d40000004000d20000004000d4000000d000d2000000d000d4000000
-- 003:4000f200000040001b00000040001b0000004000f200000040001b00000040001b000000a000f600000040001b0000004000f200000040001b00000040001b00000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b000000
-- 004:900009000000000000000000b00009000000000000000000d000c80000000000000000004000ca000000000000000000b00009000000000000000000d00009000000000000000000f000c80000000000000000006000ca000000000000000000d00009000000000000000000f000090000000000000000005000ca0000000000000000008000ca0000000000000000006000ca00000000000000000010000000000060000b000000000000000000d000ca000000000000000000000000000000
-- 005:6000e80000000000000000008000e80000000000000000009000e8000000000000000000d000e80000000000000000008000e80000000000000000009000e8000000000000000000b000e8000000000000000000f000e80000000000000000008000e8000000000000000000b000e8000000000000000000d000e80000000000000000005000ea000000000000000000d000e8000000000000000000000000000000d000090000000000000000006000ea000000000000000000000000000000
-- 006:9000d20000009000d40000009000d20000009000d40000009000d20000009000d40000009000d20000009000d4000000b000d2000000b000d4000000b000d2000000b000d4000000b000d2000000b000d4000000b000d2000000b000d4000000d000d2000000d000d4000000d000d2000000d000d4000000d000d2000000d000d4000000d000d2000000d000d40000006000d20000006000d40000006000d20000006000d40000006000d20000006000d4000000d000d2000000d000d4000000
-- 007:4000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f2000000a000f6000000a000f60000004000f2000000a000f60000004000f2000000a000f6000000a000f6000000
-- 008:8000c8000000000000000000b000c8000000000000000000d000c8000000000000000000e00009000000d00009000000000000000000b000090000000000000000008000c80000000000000000000000000000006000090000000000000000008000c8000000000000000000000000000000000000000000b000c8000000000000000000d000c8000000000000000000f000c8000000000000000000000000000000d00009000000000000000000b00009000000000000000000800009000000
-- 009:000000000000f000e60000000000000000000000000000000000000000008000e8000000000000000000000000000000000000000000f000e60000000000000000000000000000000000000000006000e80000000000000000000000000000000000000000004000e8000000000000000000000000000000000000000000b000e6000000000000000000000000000000000000000000f000e6000000000000000000000000000000000000000000a000e6000000000000000000000000000000
-- 010:8000d20000008000d40000008000d20000008000d4000000b000d2000000b000d4000000d000d2000000d000d40000008000d20000008000d40000008000d20000008000d40000006000d20000006000d40000008000d20000008000d40000004000d20000004000d40000004000d20000004000d40000006000d20000006000d40000006000d20000006000d40000008000d20000008000d4000000b000d2000000b000d4000000f000d2000000f000d40000006000d20000006000d4000000
-- 011:4000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f60000004000f20000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f600000040001b0000004000f200000040001b000000a000f60000004000f20000004000f200000040001b000000a000f600000040001b000000
-- 012:8000c8000000000000000000b000c8000000000000000000d000c8000000000000000000f000c80000000000000000006000ca000000000000000000000000000000f00009000000000000000000d000c8000000000000000000000000000000b000c8000000000000000000d000c8000000000000000000f000c800000000000000000060000b0000000000000000008000ca0000000000000000000000000000000000000000006000ca000000000000000000f00009000000000000000000
-- 013:f000c800000000000000000000000000000000000000000000000000000040000b000000000000000000f000c8000000000000000000000000000000d00009000000000000000000b000c8000000000000000000d00009000000000000000000f000c8000000000000000000000000000000000000000000000000000000a000c8000000000000000000000000000000000000000000600009000000000000000000800009000000000000000000a000c8000000000000000000000000000000
-- 014:b000c8000000000000000000000000000000d000c8000000000000000000000000000000f000c800000000000000000000000000000040000b0000000000000000006000ca000000000000000000000000000000000000000000000000000000f000c8000000000000000000000000000000000000000000000000000000d000c8000000000000000000000000000000f000c8000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000
-- 015:8000ca00000000000000000000000000000000000000000000000000000060000b0000000000000000004000ca000000000000000000000000000000f000c8000000000000000000000000000000000000000000d00009000000000000000000b000c8000000000000000000000000000000d00009000000000000000000f000c8000000000000000000000000000000000000000000000000000000a000c8000000000000000000000000000000000000000000000000000000000000000000
-- 016:b000c8000000000000000000000000000000d000c8000000000000000000000000000000f000c80000000000000000000000000000006000ca00000000000000000000000000000040000b000000000000000000f000c8000000000000000000000000000000000000000000d000c8000000000000000000000000000000000000000000a000c80000000000000000000000000000000000000000008000c8000000000000000000000000000000000000000000000000000000000000000000
-- 017:b000e8000000000000000000000000000000000000000000000000000000d000e8000000000000000000b000e80000000000000000000000000000000000000000000000000000008000e8000000000000000000000000000000000000000000b000e80000000000000000000000000000000000000000000000000000006000e8000000000000000000000000000000000000000000f000e60000000000000000000000000000000000000000006000e8000000000000000000000000000000
-- 018:8000d20000008000d40000008000d20000008000d40000008000d20000008000d40000008000d20000008000d40000006000d20000006000d40000006000d20000006000d40000006000d20000006000d40000006000d20000006000d40000004000d20000004000d40000004000d20000004000d40000004000d20000004000d40000004000d20000004000d40000006000d20000006000d40000006000d20000006000d4000000f000d2000000f000d40000006000d20000006000d4000000
-- 019:a00009000000000000a00009000000000000800009000000a000c8000000000000000000000000000000000000000000a00009000000000000a00009000000000000800009000000a000c8000000000000000000000000000000000000000000a00009000000000000a00009000000000000800009000000a000c8000000000000000000000000000000000000000000d00009000000000000000000c00009000000000000000000800009000000000000000000a000c8000000000000000000
-- 020:6000ca00000000000000000060000b00000000000000000050000b000000000000000000f000090000000000000000005000ca000000000000000000000000000000000000000000d000c8000000000000000000000000000000000000000000a000c8000000000000000000000000000000c00009000000000000000000d000c8000000000000000000000000000000f000c80000000000000000000000000000000000000000005000ca000000000000000000000000000000000000000000
-- 021:6000ca00000000000000000060000b00000000000000000050000b000000000000000000f000090000000000000000005000ca000000000000000000000000000000000000000000a000ca0000000000000000000000000000000000000000008000ca0000000000000000000000000000000000000000005000ca000000000000000000000000000000000000000000f000c800000000000000000000000000000050000b000000000000000000d000c8000000000000000000000000000000
-- 022:d000c8000000000000000000000000000000f000090000000000000000005000ca0000000000000000000000000000006000ca00000000000000000000000000000080000b000000000000000000a000ca000000000000000000000000000000c000ca000000000000000000000000000000000000000000a000ca00000000000000000080000b0000000000000000005000ca000000000000000000000000000000f00009000000000000000000c000c8000000000000000000000000000000
-- 023:d000e8000000000000000000000000000000000000000000c000e8000000000000000000000000000000000000000000d000e80000000000000000000000000000000000000000008000e80000000000000000000000000000000000000000005000e8000000000000000000000000000000000000000000000000000000a000e80000000000000000000000000000008000e8000000000000000000000000000000000000000000c000e8000000000000000000000000000000000000000000
-- 024:a000e8000000000000000000000000000000c000e8000000000000000000d000e8000000000000000000000000000000f000e80000000000000000000000000000005000ea0000000000000000006000ea0000000000000000000000000000008000ea0000000000000000000000000000000000000000005000ea000000000000000000000000000000000000000000d000e80000000000000000000000000000000000000000000000000000008000e8000000000000000000000000000000
-- 025:6000d20000006000d40000006000d20000006000d40000006000d20000006000d40000006000d20000006000d40000008000d20000008000d40000008000d20000008000d40000008000d20000008000d40000008000d20000008000d4000000a000d2000000a000d4000000a000d2000000a000d4000000a000d2000000a000d4000000a000d2000000a000d4000000a000d2000000a000d40000008000d20000008000d40000005000d20000005000d40000008000d20000008000d4000000
-- 026:f000c8000000000000000000d00009000000000000000000b000c8000000000000000000800009000000000000000000b000c8000000000000000000d00009000000000000000000f000c8000000000000000000000000000000d00009000000000000000000b000090000000000000000008000c80000000000000000000000000000006000090000000000000000008000c8000000000000000000000000000000b00009000000000000000000d000c8000000000000000000000000000000
-- 027:f000c80000000000000000006000ca0000000000000000008000ca00000000000000000000000000000060000b000000000000000000f000c8000000000000000000000000000000d00009000000000000000000b000c8000000000000000000d000c80000000000000000000000000000000000000000008000c8000000000000000000000000000000000000000000b00009000000000000000000d00009000000000000000000f000c8000000000000000000000000000000000000000000
-- 028:8000ca00000000000000000060000b000000000000000000f000c8000000000000000000d00009000000000000000000b000c8000000000000000000d00009000000000000000000f000c800000000000000000060000b0000000000000000008000ca000000000000000000000000000000b000ca00000000000000000000000000000080000b0000000000000000006000ca000000000000000000f00009000000000000000000d00009000000000000000000b000c8000000000000000000
-- 029:000000000000b000e6000000000000000000f000e60000000000000000006000e8000000000000000000f000e60000000000000000008000e6000000000000000000b000e60000000000000000004000e8000000000000000000b000e6000000000000000000a000e6000000000000000000d000e60000000000000000006000e8000000000000000000d000e6000000000000000000b000e6000000000000000000f000e60000000000000000008000e8000000000000000000f000e6000000
-- 030:8000d20000008000d40000008000d20000008000d4000000b000d2000000b000d40000008000d20000008000d40000004000d20000004000d40000004000d20000004000d40000008000d20000008000d40000004000d20000004000d40000006000d20000006000d40000006000d20000006000d4000000a000d2000000a000d40000006000d20000006000d40000008000d20000008000d40000008000d20000008000d4000000f000d2000000f000d40000006000d20000006000d4000000
-- 031:8000c8000000000000000000000000000000900009000000000000000000800009000000000000000000c000c8000000000000000000000000000000d000c8000000000000000000000000000000c000090000000000000000009000c80000000000000000000000000000008000c80000000000000000000000000000007000090000000000000000008000c8000000000000000000000000000000c00009000000000000000000f000c8000000000000000000000000000000000000000000
-- 032:f000c800000000000000000000000000000040000b000000000000000000f000c8000000000000000000000000000000d000c8000000000000000000000000000000c000090000000000000000009000c80000000000000000000000000000008000c8000000000000000000000000000000900009000000000000000000c000c8000000000000000000000000000000f000c80000000000000000000000000000008000ca00000000000000000000000000000060000b000000000000000000
-- 033:8000ca00000000000000000000000000000090000b0000000000000000008000ca0000000000000000000000000000006000ca00000000000000000000000000000040000b000000000000000000f000c80000000000000000000000000000004000ca000000000000000000f00009000000000000000000d00009000000000000000000c000c80000000000000000009000090000000000000000008000c8000000000000000000000000000000f000c8000000000000000000000000000000
-- 034:f000e60000000000000000000000000000000000000000008000e80000000000000000000000000000000000000000004000e80000000000000000000000000000000000000000009000e8000000000000000000000000000000000000000000f000e60000000000000000000000000000000000000000008000e80000000000000000000000000000000000000000007000e8000000000000000000000000000000000000000000f000e6000000000000000000000000000000000000000000
-- 035:8000d20000008000d40000008000d20000008000d40000009000d20000009000d40000008000d20000008000d40000008000d20000008000d40000008000d20000008000d4000000c000d2000000c000d4000000f000d2000000f000d40000004000d20000004000d40000004000d20000004000d4000000f000d2000000f000d4000000d000d2000000d000d40000009000d20000009000d40000009000d20000009000d40000008000d20000008000d4000000f000d2000000f000d4000000
-- 036:4000f20000004000f20000004000f200000040001b000000a000f600000040001b000000a000f600000040001b0000004000f20000004000f20000004000f200000040001b000000a000f600000040001b000000a000f600000040001b0000004000f20000004000f20000004000f200000040001b000000a000f600000040001b000000a000f600000040001b0000004000f20000004000f20000004000f200000040001b000000a000f600000040001b000000a000f600000040001b000000
-- 037:800009000000000000000000900009000000000000000000b00009000000000000000000c00009000000000000000000d00009000000000000000000f0000900000000000000000040000b00000000000000000060000b0000000000000000008000ca00000000000000000000000000000000000000000060000b00000000000000000040000b000000000000000000f000c8000000000000000000000000000000000000000000c000c8000000000000000000000000000000000000000000
-- 038:80000b000000000000000000f0000900000000000000000040000b000000000000000000d00009000000000000000000f00009000000000000000000c00009000000000000000000d000090000000000000000009000090000000000000000008000c8000000000000000000000000000000000000000000f0000900000000000000000060000b0000000000000000008000ca00000000000000000000000000000000000000000000000000000090000b000000000000000000000000000000
-- 039:800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000800007000000c00007000000f00007000000800009000000
-- 040:800009000000000000000000b00009000000000000000000d000c8000000000000000000000000000000000000000000f0000900000000000000000060000b0000000000000000008000ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060000b0000000000000000008000ca000000000000000000000000000000000000000000000000000000000000000000b000ca000000000000000000000000000000000000000000
-- 041:800009000000000000000000800009000000000000000000b000c8000000000000000000d000c8000000000000000000800009000000000000000000b00009000000000000000000f000c8000000000000000000d000090000000000000000006000090000000000000000006000090000000000000000009000c8000000000000000000b000c8000000000000000000d00009000000000000000000f00009000000000000000000b000c80000000000000000008000c8000000000000000000
-- 042:000000000000f000e60000000000000000000000000000000000000000006000e8000000000000000000000000000000000000000000f000e60000000000000000000000000000000000000000008000e8000000000000000000000000000000000000000000d000e60000000000000000000000000000000000000000004000e80000000000000000000000000000000000000000006000e8000000000000000000000000000000000000000000f000e6000000000000000000000000000000
-- 043:8000d20000008000d40000008000d20000008000d4000000b000d2000000b000d4000000d000d2000000d000d40000008000d20000008000d40000008000d20000008000d4000000f000d2000000f000d4000000d000d2000000d000d40000006000d20000006000d40000006000d20000006000d40000009000d20000009000d4000000b000d2000000b000d4000000d000d2000000d000d4000000f000d2000000f000d4000000b000d2000000b000d40000008000d20000008000d4000000
-- 044:400009000000000000000000800009000000000000000000b000c80000000000000000000000000000004000ca000000000000000000000000000000000000000000000000000000f000090000000000000000004000ca00000000000000000000000000000000000000000060000b0000000000000000008000ca000000000000000000000000000000000000000000000000000000000000000000b000ca000000000000000000000000000000000000000000000000000000000000000000
-- 045:9000ca00000000000000000000000000000080000b0000000000000000000000000000006000ca0000000000000000000000000000004000ca000000000000000000000000000000f000090000000000000000004000ca000000000000000000000000000000000000000000b000c80000000000000000000000000000000000000000004000ca0000000000000000000000000000000000000000000000000000008000ca000000000000000000000000000000000000000000000000000000
-- 046:8000e8000000000000000000000000000000000000000000b000e80000000000000000000000000000008000e8000000000000000000000000000000000000000000000000000000000000000000000000000000b000e8000000000000000000000000000000000000000000000000000000000000000000b000e8000000000000000000000000000000000000000000000000000000000000000000f000e8000000000000000000000000000000000000000000000000000000000000000000
-- 047:4000d20000004000d40000004000d20000004000d40000008000d20000008000d4000000b000d2000000b000d40000009000d20000009000d40000009000d20000009000d4000000d000d2000000d000d40000009000d20000009000d4000000b000d2000000b000d4000000b000d2000000b000d4000000f000d2000000f000d4000000b000d2000000b000d40000004000d20000004000d40000004000d20000004000d4000000b000d2000000b000d40000004000d20000004000d4000000
-- </PATTERNS>

-- <TRACKS>
-- 000:180301581702982b03d82b030000000000000000000000000000000000000000000000000000000000000000000000004000ff
-- 001:e84313f84313094313194313000000000000000000000000000000000000000000000000000000000000000000000000a000ff
-- 002:416a13516a13616a13756a13000000000000000000000000000000000000000000000000000000000000000000000000e000ff
-- 003:b97f13c97f13d97f13c97f13000000000000000000000000000000000000000000000000000000000000000000000000c000ff
-- 004:0e84691e84692e84691e84690000000000000000000000000000000000000000000000000000000000000000000000000100ef
-- 005:62a46972a469000000000000000000000000000000000000000000000000000000000000000000000000000000000000c100ef
-- 006:9eac23aeac230000000000000000000000000000000000000000000000000000000000000000000000000000000000002100ef
-- 007:deb033eeb0330000000000000000000000000000000000000000000000000000000000000000000000000000000000006000ff
-- </TRACKS>

-- <PALETTE>
-- 000:141624f4f4f8c8cee25a627dffc89cd4885c6b3a28e62e3df58025ffd93b52d6601b7a442c9cf51b38946cf0ff882e96
-- </PALETTE>
