#!/usr/bin/env python3
"""
STREET FIGHTER II': CHAMPION EDITION 80 — Single-Source Cartridge Builder (.lua & .tic)

Generates sf2_ce_80.lua and binary sf2_ce_80.tic featuring:
- Neo Geo Pocket Color (Match of the Millennium) Chibi/SD Pixel Art & 1px Dark Outlines
- Full 12-Fighter Roster: RYU, KEN, CHUN-LI, GUILE, BLANKA, E.HONDA, ZANGIEF,
  DHALSIM, BALROG, VEGA, SAGAT, M.BISON (with 1P/2P Champion Edition palettes)
- Authentic SF2 Combat Engine: CE Normal & HF Turbo speed, 20f Motion Input Buffer
  with Positive + Negative Edge, 12f Charge Partition, 360° SPD, Hitstop, Normal->Special
  Cancels, 3f Pre-Jump Squat, High/Low/Overhead/Cross-up/Throw matrix, Chip Damage,
  Corner Pushback Transfer, Hidden Stun/Dizzy + Mash Recovery
- 12 Home Stages + Crush the Car Bonus Stage + 1P Arcade / 2P Versus / Training / Attract Mode
- Complete TIC-80 Audio Assets (<WAVES>, <SFX>, <PATTERNS>, <TRACKS>)
"""
import json
import os
import re
import struct
from pathlib import Path

ROOT = Path(__file__).parent
VERSION = json.loads((ROOT / "package.json").read_text())["version"]

# 16-Color NGPC-inspired SF2 Master Palette
NGPC_SF2_16 = [
    (0x14, 0x16, 0x24),  # 0: Deep Ink / Outline / BG Void
    (0xF4, 0xF4, 0xF8),  # 1: Pure White (Ryu Gi, Honda Face, Flash)
    (0xC8, 0xCE, 0xE2),  # 2: Cool Silver / Gi Shade / Vega Claw
    (0x5A, 0x62, 0x7D),  # 3: Steel Slate / Concrete / Dark Metal
    (0xFF, 0xC8, 0x9C),  # 4: Light Skin
    (0xD4, 0x88, 0x5C),  # 5: Warm Tan / Skin Shadow
    (0x6B, 0x3A, 0x28),  # 6: Mahogany / Hair / Wood / Balrog Skin
    (0xE6, 0x2E, 0x3D),  # 7: Arcade Crimson Red (Ken, Ryu Band, HUD Red)
    (0xF5, 0x80, 0x25),  # 8: Blazing Orange (Blanka Hair, Yoga Fire)
    (0xFF, 0xD9, 0x3B),  # 9: Electric Gold (SF2 HP Yellow, Guile Hair)
    (0x52, 0xD6, 0x60),  # 10: Emerald Green (Blanka Skin, Guile Camo)
    (0x1B, 0x7A, 0x44),  # 11: Deep Forest Green (Camo Shade, Jungle)
    (0x2C, 0x9C, 0xF5),  # 12: Arcade Sky Blue (Chun Qipao, Sky)
    (0x1B, 0x38, 0x94),  # 13: Deep Cobalt / Royal Blue (Ryu 2P, Night)
    (0x6C, 0xF0, 0xFF),  # 14: Electric Cyan (Hadouken, Sonic Boom, Sparks)
    (0x88, 0x2E, 0x96),  # 15: Psycho Purple (M.Bison, Vega Trim, Night)
]

# 8x8 & Multi-Tile NGPC Pixel-Art Assets (hex indices 0..f, 0=transparent colorkey)
# Palette Convention inside Character Sprites (remapped at runtime via set_char_pal):
#   0 = Transparent (colorkey)
#   f = Ink Black Outline & Pupils (remapped -> 0)
#   1 = Pure White (eye sclera, fangs, teeth, highlight, Vega mask, Honda white makeup, Chun-Li boots/buns)
#   2 = Costume Primary Highlight (-> p[3])   3 = Costume Shadow (-> p[4])
#   4 = Skin Highlight (-> p[1])              5 = Skin Shadow (-> p[2])
#   7 = Character Accent (-> p[5])            6 = Hair / Trim (-> p[6])
#   e = Special / Scar / Metal (-> p[7])      8 = Orange   9 = Gold   d = Deep Cobalt
SPRITE_PATTERNS = {
    1: [
        "000cc000",
        "00ceec00",
        "0ce11ec0",
        "ce1111ec",
        "ce1111ec",
        "0ce11ec0",
        "00ceec00",
        "000cc000",
    ],
    2: [
        "00c00c00",
        "c0ceec0c",
        "0ce11ec0",
        "cce11ecc",
        "0ce11ec0",
        "c0ceec0c",
        "00c00c00",
        "00000000",
    ],
    3: [
        "00ee1100",
        "0e1111e0",
        "e119911e",
        "e199991e",
        "e119911e",
        "0e1111e0",
        "00ee1100",
        "00000000",
    ],
    4: [
        "0e111100",
        "e19991e0",
        "1991191e",
        "1991191e",
        "e19991e0",
        "0e111100",
        "00000000",
        "00000000",
    ],
    5: [
        "90011009",
        "09088090",
        "00911900",
        "18111181",
        "18111181",
        "00911900",
        "09088090",
        "90011009",
    ],
    6: [
        "00eeee00",
        "0ec11ce0",
        "ec1001ce",
        "e100001e",
        "e100001e",
        "ec1001ce",
        "0ec11ce0",
        "00eeee00",
    ],
    7: [
        "00090000",
        "00090000",
        "99919990",
        "09111900",
        "00919000",
        "09000900",
        "90000090",
        "00000000",
    ],
    8: [
        "00099000",
        "00911980",
        "99111900",
        "09999000",
        "00909000",
        "00000000",
        "00000000",
        "00000000",
    ],
    9: [
        "00099000",
        "00911900",
        "99111199",
        "09199190",
        "00999900",
        "09900990",
        "90000009",
        "00000000",
    ],
    10: [
        "00877000",
        "08919800",
        "89111970",
        "79199870",
        "08988700",
        "00777000",
        "00000000",
        "00000000",
    ],
    11: [
        "00ffff00",
        "0f3223f0",
        "f321123f",
        "f21ff12f",
        "f21ff12f",
        "f321123f",
        "0f3223f0",
        "00ffff00",
    ],
    12: [
        "f666666f",
        "65555566",
        "65855856",
        "f333333f",
        "65588556",
        "65855856",
        "66555556",
        "f666666f",
    ],
    # 13: Dither checkerboard 8x8 (color 1=overlay, 0=transparent)
    13: [
        "10101010",
        "01010101",
        "10101010",
        "01010101",
        "10101010",
        "01010101",
        "10101010",
        "01010101",
    ],
    # 14: Japanese roof shingle tile 8x8
    14: [
        "f33ff33f",
        "322ff223",
        "333ff333",
        "ffffffff",
        "3ff33ff3",
        "2ff22ff2",
        "3ff33ff3",
        "ffffffff",
    ],
    # 15: Cobblestone / brick tile 8x8
    15: [
        "2222f222",
        "5555f555",
        "5333f333",
        "ffffffff",
        "f2222f22",
        "f5555f55",
        "f3333f33",
        "ffffffff",
    ],
    # 16: Sakura / tree blossom foliage 8x8
    16: [
        "00f717f0",
        "0f71417f",
        "f741741f",
        "f477174f",
        "0f7474f0",
        "00ffff00",
        "00000000",
        "00000000",
    ],
    # 17: Wave crest 8x8
    17: [
        "00011000",
        "001cc100",
        "01ccdd10",
        "1ccdddd1",
        "ccdddddc",
        "00000000",
        "00000000",
        "00000000",
    ],
    # 18: Punch Impact Wave / Speed Burst 8x8
    18: [
        "000ff110",
        "00f991ef",
        "11f911ef",
        "ff9911ef",
        "ff9911ef",
        "11f911ef",
        "00f991ef",
        "000ff110",
    ],
    # 19: Kick Crescent Slash Arc 8x8
    19: [
        "00ff1100",
        "000f1ef0",
        "0000f1ef",
        "0000f11f",
        "0000f11f",
        "0000f1ef",
        "000f1ef0",
        "00ff1100",
    ],
    # 20: Heavy / Overhead Starburst 8x8
    20: [
        "00f909f0",
        "0f91f19f",
        "f9111119",
        "0f11911f",
        "0f11911f",
        "f9111119",
        "0f91f19f",
        "00f909f0",
    ],
    # 21: Dhalsim Elastic Limb Segment 8x8
    21: [
        "00000000",
        "00000000",
        "ffffffff",
        "44544544",
        "55455455",
        "ffffffff",
        "00000000",
        "00000000",
    ],
    # 22: Dhalsim Extended Yoga Fist Tip 8x8
    22: [
        "00ffff00",
        "0f7744f0",
        "f774445f",
        "f774455f",
        "f774455f",
        "f774445f",
        "0f7744f0",
        "00ffff00",
    ],
    # 23: Vega 3-Pronged Silver Claw Slash 8x8
    23: [
        "ff111100",
        "00ffff1e",
        "ff111110",
        "00ffff1e",
        "ff111110",
        "00ffff1e",
        "00000000",
        "00000000",
    ],
}

# Multi-tile NGPC Pixel Art Sheets (base_id -> (w_tiles, h_tiles, pixel_rows))
# TIC-80 tile sheet is 16 tiles wide: row r spans [base_id + r*16 .. base_id + r*16 + w_tiles - 1]
MULTI_SPRITES = {
    # --- ROW 2..3 (32..63): 8x Fighter Heads (16x16 each, facing RIGHT) ---
    32: (2, 2, [  # RYU: tousled dark spikes, crimson hachimaki headband & knot, fierce anime eyes
        "0000ff0f0fff0000",
        "00ff66f6f666ff00",
        "0f66666666666ff0",
        "f7f77777777777f0",
        "77ff777777777ff0",
        "f70f444ff4fff4f0",
        "00f4ff1f4f1ff4f0",
        "00f411f444f1f4f0",
        "00f41f14441f14f0",
        "00f54444454445f0",
        "00f5444445544f00",
        "00f544fff4445f00",
        "000f54444445f000",
        "0000ff5444ff0000",
        "00000f5445f00000",
        "000000ffff000000",
    ]),
    34: (2, 2, [  # KEN: swept-up golden layered anime spikes (1px black top outline), fierce eyes & grin
        "0ffffffffffff000",
        "f666f666f6666ff0",
        "f6696666669666ff",
        "f66666666666666f",
        "f66ff666ff66fff0",
        "0f6f444ff4fff4f0",
        "0f6f4ff1f4f1ff4f",
        "0f5f411f444f1f4f",
        "00ff41f14441f14f",
        "00f54444454445f0",
        "00f54444444445f0",
        "00f54f111f444f00",
        "000f54444444f000",
        "0000ff5444ff0000",
        "00000f5445f00000",
        "000000ffff000000",
    ]),
    36: (2, 2, [  # CHUN-LI: twin white/gold silk ox-horn buns with ribbons, sparkling anime eyes
        "00000ffffff00000",
        "f11ff666666ff11f",
        "191f66666666f191",
        "111f66ff66ff6f11",
        "f19f6f444444ff1f",
        "0f9f4f1ff4ff1f4f",
        "0f6f4f11f4f11f4f",
        "00ff41f1f441ff4f",
        "00f5411144411f4f",
        "00f54744454474f0",
        "000f444444444f00",
        "000f544ff444f000",
        "0000f544444f0000",
        "00000ff44ff00000",
        "000000ffff000000",
        "0000000000000000",
    ]),
    38: (2, 2, [  # GUILE: towering flared golden flat-top brush hair, sharp military jaw
        "f99999999999999f",
        "f98999999999998f",
        "f99899999999989f",
        "0f988999999989f0",
        "0f88ff8888ff8f00",
        "00ff444ff4fff4f0",
        "00f4ff1f4f1ff4f0",
        "00f411f444f1f4f0",
        "00f54444454445f0",
        "00f5444444444f00",
        "00f544fff444f000",
        "00f554444445f000",
        "000ff544445ff000",
        "0000ff5444ff0000",
        "00000ffffff00000",
        "0000000000000000",
    ]),
    40: (2, 2, [  # BLANKA: wild jagged blazing mane, emerald beast face, glowing eyes & lower fangs
        "0ff6f66ff66f6f00",
        "f6666666666666f0",
        "f66866ff666666ff",
        "f66f4444ff4fff4f",
        "f6ff4ff9f4f9ff4f",
        "f6f441f1f4f1f14f",
        "f6f441114441114f",
        "0ff54444ff4445f0",
        "00f5444444444f00",
        "00f51fffff1fff00",
        "00f5414441445f00",
        "000ff444444ff000",
        "0000f544445f0000",
        "00000f5445f00000",
        "000000ffff000000",
        "0000000000000000",
    ]),
    42: (2, 2, [  # E.HONDA: black sumo topknot, white kabuki base & crimson kumadori paint
        "000000ffff000000",
        "0000ffddddff0000",
        "00ffddffffddff00",
        "0fdddffffffdddf0",
        "0fdf111ff111fdf0",
        "0f17ff1f11f171f0",
        "0f711ff111ff17f0",
        "0f171111111171f0",
        "0f117111111711f0",
        "0f111144441111f0",
        "00f144ffff441f00",
        "00f4444444444f00",
        "000f54444445f000",
        "0000ff5445ff0000",
        "000000ffff000000",
        "0000000000000000",
    ]),
    44: (2, 2, [  # ZANGIEF: tall jagged mohawk, thick bushy full beard & fierce bared teeth
        "000000ffff000000",
        "00000f6666f00000",
        "000ff666666ff000",
        "00f54ffffff45f00",
        "0f54ff1f4f1ff4f0",
        "0f5411f444f1f4f0",
        "0f544444544445f0",
        "0f6f64444446f6f0",
        "0f666f1111f666f0",
        "0f666ffffff666f0",
        "00f6666666666f00",
        "00f6666666666f00",
        "000f66666666f000",
        "0000ff6666ff0000",
        "000000ffff000000",
        "0000000000000000",
    ]),
    46: (2, 2, [  # DHALSIM: sacred bald dome, 3 yoga forehead stripes, white eyes, skull beads
        "00000ffffff00000",
        "000ff444444ff000",
        "00f5411771144f00",
        "00f5444774444f00",
        "00f54ff44ffff4f0",
        "00f4111444111f00",
        "00f5411454114f00",
        "00f5444444444f00",
        "000f544ff445f000",
        "000f54444445f000",
        "0000ff5445ff0000",
        "00ff1f1ff1f1ff00",
        "0f11f1f11f1f11f0",
        "00ff0ff00ff0ff00",
        "0000000000000000",
        "0000000000000000",
    ]),

    # --- ROW 4..5 (64..95): Remaining 4 Fighter Heads + 4x 16x16 FX/Prop Sprites ---
    64: (2, 2, [  # BALROG: box black flat-top fade, gold hoop earring, scowling boxer brow
        "000fffffffff0000",
        "00fffffffffff000",
        "00fffffffffff000",
        "00f4544444445f00",
        "00f4ff1f4f1ff4f0",
        "0f9f411f44f1f4f0",
        "0f4f454444444f00",
        "00f4444fff444f00",
        "00f4444444444f00",
        "00f544fff4445f00",
        "000f54444445f000",
        "0000ff5444ff0000",
        "00000f5445f00000",
        "000000ffff000000",
        "0000000000000000",
        "0000000000000000",
    ]),
    66: (2, 2, [  # VEGA: pure white porcelain matador mask, menacing dark eye slits, flowing blonde locks
        "0000ffffffff0000",
        "00ff99999999ff00",
        "0f998111111899f0",
        "f98f11111111f89f",
        "f98f11811811f89f",
        "f9f1f1ff1ff11f9f",
        "f9f11ff11ff11f9f",
        "f9f1111111111f9f",
        "f9f1e11ff11e1f9f",
        "f98f1e1111e1f89f",
        "0f9ff111111ff9f0",
        "0f98ff1111ff89f0",
        "0f988ffffff889f0",
        "0f98f000000f89f0",
        "00ff00000000ff00",
        "0000000000000000",
    ]),
    68: (2, 2, [  # SAGAT: towering bald Muay Thai head, thick black eyepatch + strap, grimace
        "00000ffffff00000",
        "000ff444444ff000",
        "00f5444444444f00",
        "00f5ff444f444f00",
        "00ffdfd44ffff4f0",
        "00f4ffff4f1ff4f0",
        "00f41ff1ff1f4f00",
        "00f54ff444444f00",
        "00f5444fff445f00",
        "000f54111145f000",
        "000f54444445f000",
        "0000ff5445ff0000",
        "00000f5445f00000",
        "000000ffff000000",
        "0000000000000000",
        "0000000000000000",
    ]),
    70: (2, 2, [  # M.BISON: peaked Shadaloo cap, winged skull crest, glowing white eyes, wicked grin
        "000fffffffffff00",
        "00f22229922222f0",
        "0f222991992222f0",
        "f3322299922223f0",
        "0fffffffffffffff",
        "000ffdddddddffff",
        "00f5f11f4f11f4f0",
        "00f5411f4f114f00",
        "00f5444444444f00",
        "00f54f11111f4f00",
        "000f54ffff45f000",
        "0000ff5445ff0000",
        "00000f5445f00000",
        "000000ffff000000",
        "0000000000000000",
        "0000000000000000",
    ]),
    72: (2, 2, [  # 16x16 Hadouken surge fireball (col 12=core rim, 14=glow, 1=white)
        "000000ccccc00000",
        "0000ccceeeccc000",
        "00ccceeeeee1cc00",
        "0cceeeee11111ec0",
        "ccceee11111111cc",
        "ceeee1111111111e",
        "ceee11111111111e",
        "cee111111111111e",
        "cee111111111111e",
        "ceee11111111111e",
        "ceeee1111111111e",
        "ccceee11111111cc",
        "0cceeeee11111ec0",
        "00ccceeeeee1cc00",
        "0000ccceeeccc000",
        "000000ccccc00000",
    ]),
    74: (2, 2, [  # 16x16 Sonic Boom / Tiger crescent aura
        "0000eeee11000000",
        "00eee11111ee0000",
        "0ee119999111e000",
        "e119991199911e00",
        "e199110011991e00",
        "0e99100001991e00",
        "00e9100001991e00",
        "00e9100001991e00",
        "00e9100001991e00",
        "0e99100001991e00",
        "e199110011991e00",
        "e119991199911e00",
        "0ee119999111e000",
        "00eee11111ee0000",
        "0000eeee11000000",
        "0000000000000000",
    ]),
    76: (2, 2, [  # 16x16 Multi-point NGPC Hit Spark
        "9000001001000009",
        "0900001881000090",
        "0090011111100900",
        "0009119999119000",
        "0001191111911000",
        "1111911111191111",
        "0881911111191880",
        "0881911111191880",
        "1111911111191111",
        "0001191111911000",
        "0009119999119000",
        "0090011111100900",
        "0900001881000090",
        "9000001001000009",
        "0000000000000000",
        "0000000000000000",
    ]),
    78: (2, 2, [  # 16x16 Wooden Destructible Barrel / Crate
        "00ffffffffffff00",
        "0f668666668666f0",
        "f68666666666686f",
        "ffffffffffffffff",
        "f33333333333333f",
        "f668666ff666866f",
        "f66666f66f66666f",
        "f66666666666666f",
        "f66866666666866f",
        "f66666f66f66666f",
        "f666666ff666666f",
        "f33333333333333f",
        "ffffffffffffffff",
        "0f666866668666f0",
        "00ffffffffffff00",
        "0000000000000000",
    ]),

    # --- ROW 6..7 (96..127): 5x Fighter Bodies (24x16 each, facing RIGHT) ---
    96: (3, 2, [  # Std Martial Arts Gi Idle 1 (wide stance, gi V-neck, belt, twin fists)
        "0000000ff44444ff00000000",
        "000000f22f444f22f0000000",
        "00000f2222f4f2222ff00000",
        "000ff222222f222f77f00000",
        "00f44f32222222ff774f0000",
        "0f444f3222222f22f44f0000",
        "0f77ff3332222f22fff00000",
        "00fff0ffffffff0000000000",
        "00000f7777f777f000000000",
        "00000f2227f7222f00000000",
        "0000f3222f0f2222f0000000",
        "000f3222f000f2222f000000",
        "00f3222f00000f2232f00000",
        "00f444f0000000f444f00000",
        "0f4455f00000000f445f0000",
        "0ffffff00000000fffff0000",
    ]),
    99: (3, 2, [  # Std Martial Arts Gi Idle 2 (breathing shift: chest dips 1px, fists bob)
        "00000000ffffffff00000000",
        "0000000ff44444ff00000000",
        "000000f22f444f22ff000000",
        "0000ff2222f4f22f77f00000",
        "000f44f3222f222ff74f0000",
        "00f444f3222222f22f4f0000",
        "00f77ff3332222f22ff00000",
        "000fff0ffffffff000000000",
        "00000f7777f777f000000000",
        "00000f2227f7222f00000000",
        "0000f3222f0f2222f0000000",
        "000f3222f000f2222f000000",
        "00f3222f00000f2232f00000",
        "00f444f0000000f444f00000",
        "0f4455f00000000f445f0000",
        "0ffffff00000000fffff0000",
    ]),
    102: (3, 2, [  # Walk Stride (crossed stepping legs, swinging fists)
        "0000000ff44444ff00000000",
        "000000f22f444f22f0000000",
        "00000f2222f4f2222f000000",
        "0000f222222f22f77ff00000",
        "000f322222222ff44f000000",
        "00f44f3322222f22f0000000",
        "00f7f0f77777ff0000000000",
        "000f0f2227f722f000000000",
        "00000f322222222f00000000",
        "000000f3222f2222f0000000",
        "0000000f22f0f222f0000000",
        "000000f22f000f22f0000000",
        "00000f22f00000f22f000000",
        "0000f44f000000f444f00000",
        "000f445f000000f445f00000",
        "000ffff0000000fffff00000",
    ]),
    105: (3, 2, [  # Crouch / Low Guard Pose
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "0000000ff44444ff00000000",
        "00000ff22f444f22f0000000",
        "0000f22222f4f222ff000000",
        "000f3222222f22f774f00000",
        "00f44f3322222ff77f000000",
        "00f7ff7777777f0ff0000000",
        "0000f22227f2222f00000000",
        "000f3222f00f2222f0000000",
        "00f3222f0000f2222f000000",
        "00f322f000000f223f000000",
        "0f444f00000000f444f00000",
        "0f455f00000000f445f00000",
        "0fffff00000000fffff00000",
    ]),
    108: (3, 2, [  # Punch / Hadouken Cast Lunge
        "000000ff44444ff000000000",
        "00000f22f444f22ff0000000",
        "0000f2222f4f22222fffffff",
        "000f322222f222222f44777f",
        "00f44f33222222222f44777f",
        "00f7ff33322222ffffffffff",
        "000ff0ffffffff0000000000",
        "00000f7777f77f0000000000",
        "0000f32227f222f000000000",
        "000f3222f00f222f00000000",
        "00f3222f0000f222f0000000",
        "0f3222f000000f222f000000",
        "0f322f00000000f222f00000",
        "f444f0000000000f444f0000",
        "f455f0000000000f445f0000",
        "fffff0000000000fffff0000",
    ]),

    # --- ROW 8..9 (128..159): 5x Fighter Attack / Defense Poses (24x16 each) ---
    128: (3, 2, [  # Rising Uppercut / Shoryuken Pose (skyward fist & driven knee)
        "0000000000000f777f000000",
        "0000000000000f744f000000",
        "000000000000f2244f000000",
        "0000000ff444f224f0000000",
        "000000f22f44222f00000000",
        "00000f32222222f000000000",
        "0000f44f32222f0000000000",
        "0000f7ff7777f00000000000",
        "000000f322222ff000000000",
        "00000f3222f2222f00000000",
        "0000f3222f00f222f0000000",
        "0000f222f000f444f0000000",
        "0000f22f00000fff00000000",
        "000f44f00000000000000000",
        "000f45f00000000000000000",
        "000ffff00000000000000000",
    ]),
    131: (3, 2, [  # High Kick / Roundhouse Pose (planted pivot leg, extended high kick)
        "00000ff4444ff00000000000",
        "0000f22f44f22f0000000000",
        "000f322222222f0000f444f0",
        "00f44f3222222f00ff22244f",
        "00f7ff332222ffff2222445f",
        "000ff0f7777f2222222ffff0",
        "00000f3222222222fff00000",
        "0000f3222222ffff00000000",
        "0000f3222fff000000000000",
        "000f3222f000000000000000",
        "000f222f0000000000000000",
        "000f22f00000000000000000",
        "00f222f00000000000000000",
        "00f444f00000000000000000",
        "00f445f00000000000000000",
        "00fffff00000000000000000",
    ]),
    134: (3, 2, [  # Low Kick / Crouch Sweep Pose
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000ff444ff00000000000",
        "00000f22f4f22f0000000000",
        "0000f32222222f0000000000",
        "000f4f3322222f0000000000",
        "000ff0f77777f00000000000",
        "00000f3222222ffff0000000",
        "0000f322222222222ffff4f0",
        "000f3222f22222222222445f",
        "00f444ff0fffffffffffffff",
        "00f455f00000000000000000",
        "00fffff00000000000000000",
        "000000000000000000000000",
    ]),
    137: (3, 2, [  # Jump Tuck / Flying Aerial Pose
        "0000000ff4444ff000000000",
        "000000f22f44f22f00000000",
        "00000f222222222f00000000",
        "0000f44f322222f77f000000",
        "0000f7ff332222f44f000000",
        "00000ff0f77777f000000000",
        "000000f32227f222fff00000",
        "00000f32222f0f22222ff000",
        "0000f3222f0000f222244f00",
        "000f444f0000000ff4445f00",
        "000f455f000000000ffff000",
        "000ffff00000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
    ]),
    140: (3, 2, [  # Guard / Cross-Arm Block Pose
        "00000000ffffffff00000000",
        "0000000ff444ff77f0000000",
        "000000f222f44f74f0000000",
        "00000f32222f4444f0000000",
        "00000f332222f774f0000000",
        "000000f332222f77f0000000",
        "0000000f77777fff00000000",
        "000000f32227f22f00000000",
        "00000f3222f0f222f0000000",
        "0000f3222f000f222f000000",
        "000f3222f00000f222f00000",
        "000f222f000000f222f00000",
        "00f444f0000000f444f00000",
        "00f455f0000000f445f00000",
        "00fffff0000000fffff00000",
        "000000000000000000000000",
    ]),

    # --- ROW 10..11 (160..191): Hit, Chun-Li Qipao, Heavy Grappler, Spin, Knockdown (24x16 each) ---
    160: (3, 2, [  # Hit Recoil (torso staggered back)
        "000000000000000000000000",
        "0000ff4444ff000000000000",
        "000f22f44f22ff0000000000",
        "0f4f3222222222f44f000000",
        "f74ff33222222f2277f00000",
        "0fff0f777777ff0fff000000",
        "00000f322227f00000000000",
        "00000f3222f22f0000000000",
        "0000f3222f0f22f000000000",
        "000f3222f000f22f00000000",
        "00f3222f0000f222f0000000",
        "00f222f000000f22f0000000",
        "0f444f0000000f444f000000",
        "0f455f0000000f445f000000",
        "0fffff0000000fffff000000",
        "000000000000000000000000",
    ]),
    163: (3, 2, [  # CHUN-LI Female Qipao + Spiked Bracelets + White Combat Boots
        "0000000ff44444ff00000000",
        "000000f22f444f22f0000000",
        "00000f22274447222ff00000",
        "000ff4f22277722f664f0000",
        "00f464f32227222ff64f0000",
        "00f66ff33227222ff0f00000",
        "000ff0f77222227f00000000",
        "00000f72227f7227f0000000",
        "0000f22f744f4472f0000000",
        "000f22f0f44f44f2f0000000",
        "0000ff0f44f0f44f00000000",
        "000000f11f000f11f0000000",
        "00000f111f000f111f000000",
        "0000f1221f000f1221f00000",
        "000f11111f000f11111f0000",
        "000fffffff000fffffff0000",
    ]),
    166: (3, 2, [  # HEAVY / SUMO / GRAPPLER Broad Bare-Chest Muscular Idle
        "000000ffffffffffff000000",
        "0000ff44444444444ff00000",
        "00ff4445444ff445444ff000",
        "0f44444444444444444f77f0",
        "f4474f45444444454f4ff74f",
        "f4444f44544444544f44fff0",
        "0ffff0f7777777777f000000",
        "00000f222229922222f00000",
        "0000f32222f22f22222f0000",
        "000f32222f0000f22222f000",
        "00f54444f000000f44445f00",
        "00f5444f00000000f4445f00",
        "0f6666f0000000000f6666f0",
        "f66666f0000000000f66666f",
        "f66666f0000000000f66666f",
        "fffffff0000000000fffffff",
    ]),
    169: (3, 2, [  # SPINNING LARIAT / TATSUMAKI Pose
        "00000000ffffffff00000000",
        "ffffffff22222222ffffffff",
        "f7444222222222222224447f",
        "ffffffff332222223fffffff",
        "00000000f777777f00000000",
        "00000000f222722f00000000",
        "0000000f322f0f222f000000",
        "000000f322f000f222f00000",
        "00000f322f00000f222f0000",
        "00000f44f0000000f444f000",
        "0000f455f0000000f445f000",
        "0000fffff0000000fffff000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
    ]),
    172: (3, 2, [  # KNOCKDOWN PRONE (Horizontal Fallen Body)
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "0000fffff000000000000000",
        "000f22222fffffffff000000",
        "0ff44f22272222222fff0000",
        "f544f322272222222222ff00",
        "f554f3322732222ffff444f0",
        "0ffff3332233222f00f455f0",
        "00000fffffffffff00fffff0",
        "000000000000000000000000",
        "000000000000000000000000",
    ]),

    # --- ROW 12..13 (192..223): Special Roll, Chun Kick, Heavy Punch, Spectators, Yoga Flame ---
    192: (3, 2, [  # CANNONBALL ROLL / PSYCHO CRUSHER Blur
        "00000000eeeeeeee00000000",
        "000000ee11111111ee000000",
        "00000e11ffffffffffe00000",
        "0000e1ff444466664ff10000",
        "000e1f4422222266444f1000",
        "000e1f6422777722464f1000",
        "000e1f6622233222666f1000",
        "0000e1ff2233322ff4f10000",
        "00000e11ffffffffffe00000",
        "000000ee11111111ee000000",
        "00000000eeeeeeee00000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
    ]),
    195: (3, 2, [  # CHUN-LI Flying/Spin Kick + White Boots
        "0000000ff4444ff000000000",
        "000000f22744722f00000000",
        "00000f322277222f00f111f0",
        "0000f44f322222ff0f11121f",
        "0000f6ff72222222ff44111f",
        "0000000f72222222444ffff0",
        "000000f222227fffff000000",
        "00000f2222fff00000000000",
        "0000f444ff00000000000000",
        "000f444f0000000000000000",
        "00f111f00000000000000000",
        "00f111f00000000000000000",
        "0f1221f00000000000000000",
        "0f1111f00000000000000000",
        "0ffffff00000000000000000",
        "000000000000000000000000",
    ]),
    198: (3, 2, [  # HEAVY / GRAPPLER Overhead Punch / Lariat Lunge
        "00000fffffffffff00000000",
        "0000f44444444444ffffffff",
        "000f4445444ff444f447777f",
        "00f4444444444444f447777f",
        "00f74f4454444444ffffffff",
        "00fff0f777777777f0000000",
        "00000f2222299222f0000000",
        "0000f32222f0f2222f000000",
        "000f54444f000f4445f00000",
        "00f5444f000000f4445f0000",
        "0f6666f00000000f6666f000",
        "f66666f00000000f66666f00",
        "fffffff00000000fffffff00",
        "000000000000000000000000",
        "000000000000000000000000",
        "000000000000000000000000",
    ]),
    202: (2, 2, [  # Spectator 1 (16x16 cheering fan in blue jacket)
        "00000ffffff00000",
        "0000f666666f0000",
        "000f64444446f000",
        "000f4f444f44f000",
        "000f44444444f000",
        "0000ff4444ff0000",
        "0ff0fcc11ccf0ff0",
        "f44ffccccccff44f",
        "0ff4fccccccf4ff0",
        "0000fccccccf0000",
        "0000fddddddff000",
        "0000f333f333f000",
        "0000f33f0f33f000",
        "000f666f0f666f00",
        "000fffff0fffff00",
        "0000000000000000",
    ]),
    204: (2, 2, [  # Spectator 2 (16x16 cheering fan in red cap & vest)
        "00000ffffff00000",
        "0000f777777fff00",
        "0000f777ffffff00",
        "0000f4f44f44f000",
        "0000f4444444f000",
        "00000ff444ff0000",
        "00f4f771177f4f00",
        "0f44f777777f44f0",
        "00ff0f7777f0ff00",
        "00000f7777f00000",
        "00000fdddfddf000",
        "0000fddddfddf000",
        "0000f33f0f33f000",
        "000f111f0f111f00",
        "000fffff0fffff00",
        "0000000000000000",
    ]),
    206: (2, 2, [  # 16x16 Yoga Flame / Intense Fireball
        "0000007780000000",
        "0007788987000000",
        "0078899198700000",
        "0789911199870000",
        "7891111119987000",
        "7891111111987000",
        "0799111111987000",
        "0078911119870000",
        "0007899998700000",
        "0078899877000000",
        "0789887000000000",
        "7887700000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]),

    # --- ROW 14..15 (224..255): 48x16 Intact Bonus Sedan (224), 48x16 Smashed Sedan (230), KO Badge (236) ---
    224: (6, 2, [  # Bonus Car Intact (48x16 sky-blue/indigo Lexus-style arcade sedan)
        "0000000000000000ffffffffffffffffffffff0000000000",
        "000000000000000f11111cccccccccccc11111f000000000",
        "00000000000000f1cee1f1eeee1fcccccce1ccf000000000",
        "0000000000000fceee11fe1ee11fcccddcc1ccf000000000",
        "000000000000fceeeeeefeeeeeeffccccccccccf00000000",
        "000fffffffffffffffffffffffffffffffffffffffffff00",
        "0fc11111cccccccccccccccccccccccccccccccccccc88f0",
        "f1cc99ccccccccccccccfccccccccccccccfccccccccc87f",
        "fcddddddddddddddddddfddddddddddddddfdddddddddddf",
        "fccccccccccccccccccccccccccccccccccccccccccccccf",
        "f99fddddfffffdddddddffffddddddddfffddddffddddf9f",
        "fddddff3322233ffdddddddddddddddff3322233ffdddddf",
        "0fffff321111123fffffffffffffffff321111123ffffff0",
        "00000f21fffff12f000000000000000f21fffff12f000000",
        "000000f3222223f00000000000000000f3222223f0000000",
        "0000000fffffff00000000000000000000fffffff0000000",
    ]),
    230: (6, 2, [  # Bonus Car Smashed / Wrecked (48x16 crumpled chassis)
        "000000000000000000000000000000000000000000000000",
        "000000000000000000000000000000000000000000000000",
        "000000000000000000ffff0000fffff00000000000000000",
        "00000000000000000f3dd3ffffc113df0000000000000000",
        "0000000000000000f3feef3f0f1e3ddf0000000000000000",
        "000000ffffff000ffddddddf0f3ddddff00000ffffff0000",
        "000ff33dd333ffff33dddd3ff3ddd333ffffff33ddd3ff00",
        "00f383dddddddd33f00dd333ddd3300fdd33333dddd37f00",
        "0f33dddd00dddd333f3dddd3f0fdddd333dd00ddddddddf0",
        "f333f33ffff333333333333333333333333ffff333f333f0",
        "fdddff3f223ffdddddddddddddddddddddff3f223ffdddf0",
        "0ffff3f11f23fffffffffffffffffffffff3f11f23ffff00",
        "00000f2ff32f00000000000000000000000f2ff32f000000",
        "000000fffff0000000000000000000000000fffff0000000",
        "000000000000000000000000000000000000000000000000",
        "000000000000000000000000000000000000000000000000",
    ]),
    236: (2, 2, [  # 16x16 Explosion Smoke / Shockwave Burst
        "0000088998800000",
        "0008899119988000",
        "0089911111199800",
        "089111ffff111980",
        "08911f3223f11980",
        "8911f221122f1198",
        "8911f211112f1198",
        "8911f321123f1198",
        "08911f3333f11980",
        "089911ffff119980",
        "0089911111199800",
        "0008899119988000",
        "0000088998800000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]),
    238: (2, 2, [  # 16x16 Rising Dragon Flame / Shoryuken Aura (tiles 238,239,254,255)
        "000000ff00000000",
        "00000f88f0000000",
        "0000f8998f00f000",
        "000f891198ff8f00",
        "00f89911998898f0",
        "0f8991111998998f",
        "0f8911111199198f",
        "f89911991111198f",
        "f89119889111998f",
        "f8911988991198f0",
        "0f89119991198f00",
        "0f8991111198f000",
        "00f89911198f0000",
        "000f889988f00000",
        "0000ff88ff000000",
        "000000ff00000000",
    ]),
}


def buf_to_tic_str(data, flip=True):
    out = []
    for b in data:
        s = f"{b:02x}"
        if flip:
            s = s[1] + s[0]
        out.append(s)
    return "".join(out)


def sprite_to_tic_hex(rows):
    text_hex = "".join(rows)
    assert len(text_hex) == 64
    raw_bytes = bytearray(32)
    for y in range(8):
        for x in range(0, 8, 2):
            p0 = int(rows[y][x], 16)
            p1 = int(rows[y][x + 1], 16)
            raw_bytes[y * 4 + (x // 2)] = (p1 << 4) | p0
    return text_hex, bytes(raw_bytes)


def assemble_tile_bank():
    """Populate all 8x8 and multi-tile pixel-art sprites into the 256-tile bank (8192B)."""
    patterns = dict(SPRITE_PATTERNS)
    for base_id, (wt, ht, rows) in MULTI_SPRITES.items():
        assert len(rows) == ht * 8, f"Sprite {base_id}: expected {ht*8} rows, got {len(rows)}"
        for r_idx, row in enumerate(rows):
            assert len(row) == wt * 8, f"Sprite {base_id} row {r_idx}: expected len {wt*8}, got {len(row)}"
        for ty in range(ht):
            for tx in range(wt):
                tid = base_id + ty * 16 + tx
                assert tid not in patterns and tid < 256, f"Sprite tile collision or overflow at tid={tid}"
                sub = [rows[ty * 8 + py][tx * 8 : (tx + 1) * 8] for py in range(8)]
                patterns[tid] = sub
    tiles_bin = bytearray(256 * 32)
    for idx in sorted(patterns.keys()):
        _, raw_bytes = sprite_to_tic_hex(patterns[idx])
        tiles_bin[idx * 32 : (idx + 1) * 32] = raw_bytes
    return bytes(tiles_bin)


def build_waveforms():
    """Build 16 TIC-80 waveforms (0=LFSR white noise, 1=square, 2=triangle, 3=saw, 4=25% pulse, 5=organ)."""
    waves = bytearray(16 * 16)
    samples_map = {
        0: [0] * 32,
        1: [0] * 16 + [15] * 16,
        2: list(range(16)) + list(range(15, -1, -1)),
        3: [i // 2 for i in range(32)],
        4: [15] * 8 + [0] * 24,
        5: [15, 15, 13, 12, 9, 8, 12, 13, 15, 14, 10, 7, 4, 2, 0, 0] * 2,
    }
    for idx, vals in samples_map.items():
        w = bytearray(16)
        for i in range(16):
            s0 = vals[i * 2] & 0xF
            s1 = vals[i * 2 + 1] & 0xF
            w[i] = (s1 << 4) | s0
        waves[idx * 16 : (idx + 1) * 16] = w
    return bytes(waves)


def make_sfx_sample(ticks, octave=3, note=0, speed=0, pitch16x=0, reverse=0):
    if not ticks:
        return bytes(66)
    buf = bytearray(66)
    for i in range(30):
        vol, wave, chord, pitch = ticks[i] if i < len(ticks) else (0, 1, 0, 0)
        atten = max(0, min(15, 15 - vol))
        buf[i * 2] = ((wave & 0xF) << 4) | (atten & 0xF)
        buf[i * 2 + 1] = ((pitch & 0xF) << 4) | (chord & 0xF)
    buf[60] = ((reverse & 1) << 7) | ((speed & 0x7) << 4) | ((pitch16x & 1) << 3) | (octave & 0x7)
    buf[61] = note & 0xF
    return bytes(buf)


def build_sfx_samples():
    """
    SFX IDs 0..11 = Gameplay & UI SFX, 12..17 = Arcade BGM Instruments.
    """
    samples = bytearray(64 * 66)
    silent = make_sfx_sample([])
    for i in range(64):
        samples[i * 66 : (i + 1) * 66] = silent

    defs = {
        0: make_sfx_sample([(13, 4, 0, 2), (10, 4, 0, 0), (5, 2, 0, -2)], octave=4, note=4, speed=0),
        1: make_sfx_sample([(14, 4, 0, 0), (14, 4, 7, 2), (12, 1, 12, 4), (8, 2, 12, 4), (3, 2, 12, 4)], octave=4, note=9, speed=0),
        2: make_sfx_sample([(11, 0, 0, 3), (9, 0, 0, 1), (6, 0, 0, -2), (3, 0, 0, -4)], octave=3, note=0, speed=0, pitch16x=1),
        3: make_sfx_sample([(15, 0, 0, 1), (14, 3, 0, -2), (10, 0, 0, -5), (5, 1, 0, -7)], octave=3, note=0, speed=0, pitch16x=1),
        4: make_sfx_sample([(15, 0, 0, 0), (15, 3, 0, -3), (14, 0, 0, -4), (12, 3, 0, -6), (9, 0, 0, -7), (6, 3, 0, -8), (3, 0, 0, -8)], octave=2, note=4, speed=1, pitch16x=1),
        5: make_sfx_sample([(14, 4, 0, 4), (12, 1, 7, 2), (8, 2, 12, 0), (4, 2, 0, -2)], octave=4, note=2, speed=0),
        6: make_sfx_sample([(15, 0, 0, 2), (14, 4, 0, 1), (13, 4, 5, -1), (11, 1, 7, -2), (9, 3, 0, -4), (6, 3, 0, -6), (3, 0, 0, -7)], octave=3, note=7, speed=0, pitch16x=1),
        7: make_sfx_sample([(15, 4, 0, -2), (15, 4, 4, 1), (14, 3, 7, 3), (13, 1, 12, 5), (11, 4, 12, 6), (8, 1, 12, 7), (4, 2, 12, 7)], octave=3, note=9, speed=0, pitch16x=1),
        8: make_sfx_sample([(15, 0, 0, 0), (15, 3, 0, -3), (14, 0, 0, -4), (13, 3, 0, -5), (12, 0, 0, -6), (10, 0, 0, -7), (8, 3, 0, -8), (6, 0, 0, -8), (4, 0, 0, -8), (2, 0, 0, -8)], octave=2, note=0, speed=2, pitch16x=1),
        9: make_sfx_sample([(15, 3, 0, -1), (14, 0, 0, -3), (12, 3, 0, -5), (10, 0, 0, -7), (6, 3, 0, -8)], octave=2, note=7, speed=1, pitch16x=1),
        10: make_sfx_sample([(12, 2, 0, 2), (11, 4, 4, 4), (9, 2, 7, 2), (7, 4, 12, 5), (4, 2, 7, 3)], octave=4, note=7, speed=0),
        11: make_sfx_sample([(15, 4, 0, 0), (15, 4, 4, 0), (14, 4, 7, 0), (13, 1, 12, 0), (10, 1, 12, 0), (6, 2, 12, 0), (3, 2, 12, 0)], octave=4, note=0, speed=1),
        # 12: Sustained Arcade Brass / Lead (26 ticks, pulse->square->saw with subtle vibrato)
        12: make_sfx_sample(
            [
                (12, 4, 0, 0), (12, 4, 0, 0), (11, 4, 0, 0), (11, 1, 0, 0),
                (10, 1, 0, 0), (10, 1, 0, 1), (10, 1, 0, 0), (9, 1, 0, -1),
                (9, 3, 0, 0), (9, 3, 0, 1), (9, 3, 0, 0), (8, 3, 0, -1),
                (8, 3, 0, 0), (8, 3, 0, 1), (8, 3, 0, 0), (7, 3, 0, -1),
                (7, 3, 0, 0), (7, 3, 0, 1), (7, 3, 0, 0), (7, 3, 0, -1),
                (6, 3, 0, 0), (5, 3, 0, 0), (4, 2, 0, 0), (3, 2, 0, 0),
                (2, 2, 0, 0), (1, 2, 0, 0),
            ],
            octave=3, note=0, speed=1,
        ),
        # 13: Punchy Slap / Picked Bass (14 ticks, saw->organ)
        13: make_sfx_sample(
            [
                (13, 3, 0, 0), (12, 3, 0, 0), (11, 3, 0, 0), (10, 5, 0, 0),
                (9, 5, 0, 0), (8, 5, 0, 0), (7, 5, 0, 0), (6, 5, 0, 0),
                (6, 5, 0, 0), (5, 5, 0, 0), (5, 5, 0, 0), (4, 5, 0, 0),
                (3, 2, 0, 0), (2, 2, 0, 0),
            ],
            octave=1, note=0, speed=1,
        ),
        # 14: Counter-Melody / Brass Harmony Synth (20 ticks, organ->triangle)
        14: make_sfx_sample(
            [
                (10, 5, 0, 0), (10, 5, 0, 0), (9, 5, 0, 0), (8, 5, 0, 0),
                (8, 5, 0, 0), (7, 5, 0, 0), (7, 2, 0, 0), (6, 2, 0, 0),
                (6, 2, 0, 0), (5, 2, 0, 0), (5, 2, 0, 0), (4, 2, 0, 0),
                (4, 2, 0, 0), (4, 2, 0, 0), (3, 2, 0, 0), (3, 2, 0, 0),
                (3, 2, 0, 0), (2, 2, 0, 0), (2, 2, 0, 0), (1, 2, 0, 0),
            ],
            octave=3, note=0, speed=1,
        ),
        # 15: Arcade Kick + Snare Drum (tight pitch-drop transient)
        15: make_sfx_sample(
            [(13, 5, 0, 4), (11, 5, 0, 1), (9, 0, 0, -2), (7, 0, 0, -5), (5, 0, 0, -7), (3, 0, 0, -8)],
            octave=2, note=0, speed=0, pitch16x=1,
        ),
        # 16: Staccato Brass / Guitar Stab (9 ticks, crisp transient)
        16: make_sfx_sample(
            [(13, 4, 0, 0), (12, 4, 0, 0), (10, 3, 0, 0), (9, 3, 0, 0), (7, 3, 0, 0), (5, 3, 0, 0), (3, 3, 0, 0), (1, 3, 0, 0), (0, 3, 0, 0)],
            octave=3, note=0, speed=0,
        ),
        # 17: Crisp Hi-Hat / Cymbal (5 ticks high-frequency LFSR noise)
        17: make_sfx_sample(
            [(9, 0, 0, 2), (7, 0, 0, 0), (5, 0, 0, -2), (3, 0, 0, -4), (2, 0, 0, -6)],
            octave=5, note=0, speed=0,
        ),
    }
    for idx, data in defs.items():
        samples[idx * 66 : (idx + 1) * 66] = data
    return bytes(samples)


def pack_track_row(note_semi=None, octave=0, sfx_id=0, command=0, param1=0, param2=0, stop=False):
    if stop:
        note_val = 1
    elif note_semi is None:
        note_val = 0
    else:
        note_val = 4 + (note_semi % 12)
    sfxhi = (sfx_id >> 5) & 1
    sfxlow = sfx_id & 0x1F
    b0 = ((param1 & 0xF) << 4) | (note_val & 0xF)
    b1 = (sfxhi << 7) | ((command & 0x7) << 4) | (param2 & 0xF)
    b2 = ((octave & 0x7) << 5) | sfxlow
    return bytes((b0, b1, b2))


def build_music():
    """Synthesize 48 tracker patterns across 8 authentic SF2' CE themes with 1-based TIC-80 pattern references."""
    patterns = bytearray(60 * 64 * 3)
    note_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
        "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    }

    def set_row(pat_idx, row_idx, row_bytes):
        off = (pat_idx * 64 + row_idx) * 3
        patterns[off : off + 3] = row_bytes

    def set_melody(pat_idx, events, default_sfx=12):
        for ev in events:
            if len(ev) == 2:
                r, nm = ev
                sfx_id = default_sfx
            else:
                r, nm, sfx_id = ev
            if nm == "OFF":
                set_row(pat_idx, r, pack_track_row(stop=True))
            else:
                octv = int(nm[-1])
                semi = note_map[nm[:-1]]
                set_row(pat_idx, r, pack_track_row(semi, octv, sfx_id=sfx_id))

    def set_drums(pat_idx, kick_rows, snare_rows, hat_rows=()):
        for r in hat_rows:
            set_row(pat_idx, r, pack_track_row(0, 5, sfx_id=17))
        for r in kick_rows:
            set_row(pat_idx, r, pack_track_row(0, 1, sfx_id=15))
        for r in snare_rows:
            set_row(pat_idx, r, pack_track_row(6, 3, sfx_id=15))

    def set_octave_bass(pat_idx, bar_notes):
        for step, root in enumerate(bar_notes):
            r = step * 4
            semi = note_map[root]
            set_row(pat_idx, r, pack_track_row(semi, 1, sfx_id=13))
            set_row(pat_idx, r + 2, pack_track_row(semi, 2, sfx_id=13))

    # --- Track 0: SF2 Arcade Opening Theme -> Player Select (Patterns 0..12) ---
    # Frame 0: Opening Fanfare A
    set_melody(0, [
        (0, "D4", 16), (6, "D4", 16), (12, "A4", 12), (22, "OFF"),
        (24, "G4", 16), (28, "F4", 16), (32, "E4", 16), (36, "F4", 16),
        (40, "G4", 12), (48, "A4", 12), (58, "OFF"), (60, "G4", 16), (62, "A4", 16),
    ])
    set_melody(1, [
        (0, "A3", 16), (6, "A3", 16), (12, "E4", 14),
        (24, "D4", 14), (28, "C4", 14), (32, "B3", 14), (36, "C4", 14),
        (40, "D4", 14), (48, "E4", 14), (60, "D4", 14),
    ], default_sfx=14)
    set_octave_bass(2, ["D", "D", "D", "D", "Bb", "Bb", "C", "C", "D", "D", "F", "G", "A", "A", "C", "A"])
    set_drums(
        3,
        kick_rows=(0, 6, 12, 16, 24, 32, 40, 48, 56),
        snare_rows=(12, 28, 36, 44, 52, 60),
        hat_rows=(2, 4, 8, 10, 14, 18, 20, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62),
    )

    # Frame 1: Opening Skyscraper Climb & Crescendo B
    set_melody(4, [
        (0, "F4", 16), (4, "G4", 16), (8, "A4", 12), (12, "C5", 12),
        (16, "G4", 16), (20, "A4", 16), (24, "B4", 12), (28, "D5", 12),
        (32, "A4", 16), (36, "B4", 16), (40, "C#5", 12), (44, "E5", 12),
        (48, "D5", 12), (52, "OFF"), (54, "D5", 16), (58, "A5", 12),
    ])
    set_melody(5, [
        (0, "D4", 14), (4, "E4", 14), (8, "F4", 14), (12, "A4", 14),
        (16, "E4", 14), (20, "F4", 14), (24, "G4", 14), (28, "B4", 14),
        (32, "E4", 14), (36, "G4", 14), (40, "A4", 14), (44, "C#5", 14),
        (48, "A4", 14), (54, "A4", 16), (58, "D5", 14),
    ], default_sfx=14)
    set_octave_bass(6, ["F", "F", "F", "F", "G", "G", "G", "G", "A", "A", "A", "A", "D", "D", "D", "A"])
    set_drums(
        7,
        kick_rows=(0, 8, 16, 24, 32, 40, 48, 54, 58),
        snare_rows=(4, 12, 20, 28, 36, 44, 50, 52, 56, 60, 62),
        hat_rows=(2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46),
    )

    # Frames 2..3: Player Select Groove + Standard Arcade Beat (pat 11 reused cleanly)
    set_melody(8, [
        (0, "E4", 12), (4, "G4", 12), (8, "A4", 12), (12, "A#4", 16), (14, "A4", 16),
        (18, "G4", 16), (22, "E4", 12), (28, "D4", 16), (32, "E4", 12), (40, "G4", 12),
        (44, "A4", 12), (48, "B4", 12), (54, "A4", 16), (58, "G4", 16), (62, "E4", 16),
    ])
    set_melody(12, [
        (0, "E4", 12), (4, "G4", 12), (8, "A4", 12), (12, "B4", 12),
        (16, "D5", 12), (22, "B4", 16), (26, "A4", 12), (32, "G4", 12),
        (36, "A4", 12), (40, "B4", 12), (44, "D5", 16), (48, "E5", 12), (56, "D5", 12), (60, "B4", 16),
    ])
    set_melody(9, [
        (2, "B3", 14), (10, "E4", 14), (18, "B3", 14), (26, "D4", 14),
        (34, "C4", 14), (42, "G3", 14), (50, "B3", 14), (58, "F#3", 14),
    ], default_sfx=14)
    set_octave_bass(10, ["E", "E", "G", "A", "E", "E", "D", "E", "C", "C", "D", "D", "E", "G", "B", "D"])
    set_drums(
        11,
        kick_rows=(0, 8, 16, 22, 24, 32, 40, 48, 54, 56),
        snare_rows=(4, 12, 20, 28, 36, 44, 52, 60),
        hat_rows=(2, 6, 10, 14, 18, 26, 30, 34, 38, 42, 46, 50, 58, 62),
    )

    # --- Track 1: Ryu's Theme (Suzaku Castle / Japan — Patterns 13..18) ---
    set_melody(13, [
        (0, "B4", 12), (10, "C5", 16), (14, "B4", 12), (20, "A4", 16),
        (24, "G4", 12), (28, "A4", 16), (32, "B4", 12), (42, "F#4", 12),
        (50, "D4", 16), (54, "E4", 16), (58, "F#4", 12),
    ])
    set_melody(14, [
        (0, "G4", 12), (6, "A4", 12), (12, "B4", 12), (18, "C5", 16),
        (22, "D5", 12), (32, "B4", 12), (42, "A4", 12), (48, "B4", 12), (60, "OFF"),
    ])
    set_melody(15, [
        (0, "E5", 12), (10, "D5", 16), (14, "C5", 12), (20, "B4", 12),
        (28, "A4", 16), (32, "G4", 12), (38, "A4", 16), (42, "B4", 12), (52, "F#4", 12),
    ])
    set_melody(16, [
        (0, "G4", 12), (6, "A4", 12), (12, "B4", 12), (18, "D5", 12),
        (24, "C5", 16), (28, "B4", 12), (36, "A4", 12), (44, "F#4", 12), (52, "E4", 12),
    ])
    set_melody(17, [
        (0, "G4", 14), (10, "A4", 14), (14, "G4", 14), (24, "E4", 14),
        (32, "G4", 14), (42, "D4", 14), (50, "B3", 14), (58, "D4", 14),
    ], default_sfx=14)
    # Galloping 16th-note octave bass (E -> D -> C -> D)
    ryu_bass_roots = ["E"] * 8 + ["D"] * 8 + ["C"] * 8 + ["D", "D", "D", "D", "B", "B", "D", "D"]
    for step, root in enumerate(ryu_bass_roots):
        r = step * 2
        semi = note_map[root]
        set_row(18, r, pack_track_row(semi, 1 if step % 2 == 0 else 2, sfx_id=13))

    # --- Track 2: Guile's Theme (Air Force Base / USA — Patterns 19..25) ---
    set_melody(19, [
        (0, "F#4", 16), (3, "F#4", 16), (6, "E4", 16), (8, "F#4", 12),
        (16, "F#4", 16), (19, "F#4", 16), (22, "E4", 16), (24, "F#4", 12),
        (32, "F#4", 16), (35, "F#4", 16), (38, "E4", 16), (40, "F#4", 12),
        (48, "A4", 16), (52, "G#4", 16), (56, "E4", 16), (60, "F#4", 12),
    ])
    set_melody(20, [
        (0, "D5", 12), (4, "D5", 16), (8, "C#5", 16), (12, "B4", 16),
        (16, "C#5", 12), (24, "A4", 12),
        (32, "F#4", 12), (38, "G#4", 16), (42, "A4", 12),
        (48, "B4", 12), (56, "C#5", 12),
    ])
    set_melody(21, [
        (0, "D5", 12), (4, "D5", 16), (8, "C#5", 16), (12, "B4", 16),
        (16, "C#5", 12), (24, "F#5", 12),
        (32, "E5", 12), (40, "C#5", 12),
        (48, "B4", 12), (54, "C#5", 16), (58, "A4", 12),
    ])
    set_melody(22, [
        (0, "A4", 12), (6, "B4", 16), (10, "C#5", 12),
        (16, "D5", 12), (22, "E5", 16), (26, "F#5", 12),
        (32, "G#5", 12), (40, "F#5", 12), (44, "E5", 16),
        (48, "C#5", 12), (54, "B4", 16), (58, "G#4", 12),
    ])
    set_melody(23, [
        (0, "A4", 14), (8, "G#4", 14), (16, "A4", 14), (24, "E4", 14),
        (32, "C#4", 14), (42, "F#4", 14), (48, "E4", 14), (56, "G#4", 14),
    ], default_sfx=14)
    set_melody(24, [
        (0, "F#4", 14), (6, "G#4", 14), (10, "A4", 14), (16, "B4", 14),
        (22, "C#5", 14), (26, "D5", 14), (32, "E5", 14), (40, "C#5", 14),
        (48, "A4", 14), (58, "E4", 14),
    ], default_sfx=14)
    set_octave_bass(25, ["D", "D", "D", "D", "E", "E", "E", "E", "F#", "F#", "F#", "F#", "F#", "E", "C#", "E"])

    # --- Track 3: Chun-Li's Theme (World Warrior Stages — Patterns 26..30) ---
    set_melody(26, [
        (0, "B4", 12), (4, "A4", 16), (8, "G4", 12), (12, "E4", 16),
        (16, "G4", 12), (20, "A4", 16), (24, "B4", 12), (30, "A4", 16),
        (34, "G4", 16), (38, "E4", 12), (44, "D4", 16), (48, "E4", 12), (54, "G4", 16), (58, "A4", 12),
    ])
    set_melody(27, [
        (0, "B4", 12), (4, "D5", 12), (8, "E5", 12), (14, "D5", 16),
        (18, "B4", 12), (24, "A4", 16), (28, "G4", 12), (32, "A4", 12),
        (40, "E4", 12), (48, "G4", 16), (52, "A4", 16), (56, "B4", 12),
    ])
    set_melody(28, [
        (0, "E5", 12), (4, "D5", 16), (8, "B4", 12), (12, "A4", 16),
        (16, "G4", 12), (20, "A4", 16), (24, "B4", 12), (28, "D5", 16),
        (32, "E5", 12), (38, "G5", 12), (44, "E5", 16), (48, "D5", 12), (52, "B4", 16), (56, "A4", 16), (60, "G4", 12),
    ])
    set_melody(29, [
        (2, "G3", 14), (6, "B3", 14), (10, "D4", 14), (14, "B3", 14),
        (18, "E3", 14), (22, "G3", 14), (26, "C4", 14), (30, "G3", 14),
        (34, "F#3", 14), (38, "A3", 14), (42, "D4", 14), (46, "A3", 14),
        (50, "G3", 14), (54, "B3", 14), (58, "E4", 14), (62, "B3", 14),
    ], default_sfx=14)
    set_octave_bass(30, ["E", "E", "G", "E", "C", "C", "E", "C", "D", "D", "F#", "D", "E", "E", "B", "D"])

    # --- Track 4: Four Kings Boss Theme (Patterns 31..36) ---
    set_melody(31, [
        (0, "E4", 12), (6, "F4", 16), (10, "E4", 16), (14, "G#4", 12),
        (20, "A4", 12), (26, "G#4", 16), (30, "F4", 12),
        (36, "E4", 12), (42, "D#4", 16), (46, "E4", 12), (52, "G#4", 16), (56, "B4", 12),
    ])
    set_melody(32, [
        (0, "B4", 12), (6, "C5", 16), (10, "B4", 12), (16, "A4", 12),
        (22, "G#4", 16), (26, "F4", 12), (32, "E4", 12), (38, "F4", 16),
        (42, "G#4", 12), (48, "B4", 12), (54, "E5", 12), (60, "D5", 16),
    ])
    set_melody(33, [
        (0, "E5", 12), (6, "F5", 16), (10, "E5", 12), (16, "D5", 12),
        (22, "C5", 16), (26, "B4", 12), (32, "C5", 12), (36, "B4", 16),
        (40, "A4", 16), (44, "G#4", 12), (48, "F4", 16), (52, "E4", 12), (58, "B4", 12),
    ])
    set_melody(34, [
        (0, "B3", 14), (8, "E4", 14), (16, "C4", 14), (24, "F4", 14),
        (32, "B3", 14), (40, "E4", 14), (48, "D#4", 14), (56, "B3", 14),
    ], default_sfx=14)
    set_octave_bass(35, ["E", "E", "F", "E", "E", "E", "G#", "B", "C", "C", "B", "A", "F", "F", "E", "B"])
    set_drums(
        36,
        kick_rows=tuple(range(0, 64, 4)) + (2, 18, 34, 50),
        snare_rows=(8, 12, 24, 28, 40, 44, 56, 60),
        hat_rows=tuple(range(2, 64, 4)),
    )

    # --- Track 5: Critical Low-HP Pinch / Danger Theme (Patterns 37..39) ---
    set_melody(37, [
        (0, "E4", 16), (4, "F4", 16), (8, "G4", 16), (12, "G#4", 16),
        (16, "A4", 16), (20, "B4", 16), (24, "C5", 16), (28, "D5", 16),
        (32, "E5", 12), (40, "D5", 16), (44, "C5", 16), (48, "B4", 12), (56, "G#4", 12),
    ])
    set_melody(38, [
        (0, "E5", 16), (4, "B4", 16), (8, "C5", 16), (12, "A4", 16),
        (16, "B4", 16), (20, "G#4", 16), (24, "A4", 16), (28, "F4", 16),
        (32, "E4", 12), (40, "B4", 16), (44, "D5", 16), (48, "E5", 12), (58, "F5", 16),
    ])
    for step in range(32):
        arp = ("E3", "G#3", "B3", "E4")[step % 4]
        set_row(39, step * 2, pack_track_row(note_map[arp[:-1]], int(arp[-1]), sfx_id=16))

    # --- Track 6: VS Screen Fanfare & Car Smash Bonus Theme (Patterns 40..43) ---
    set_melody(40, [
        (0, "E4", 16), (4, "G4", 16), (8, "A4", 12),
        (16, "B4", 16), (20, "D5", 16), (24, "E5", 12),
        (40, "D5", 16), (44, "E5", 12), (56, "G5", 12),
    ])
    set_melody(41, [
        (0, "E4", 16), (4, "E4", 16), (8, "G4", 12), (12, "A4", 12),
        (16, "E4", 16), (20, "G4", 16), (24, "B4", 12), (28, "A4", 16),
        (32, "D4", 16), (36, "D4", 16), (40, "F4", 12), (44, "G4", 12),
        (48, "A4", 16), (52, "B4", 16), (56, "G4", 12), (60, "E4", 12),
    ])
    set_melody(42, [
        (2, "B3", 14), (10, "D4", 14), (18, "B3", 14), (26, "E4", 14),
        (34, "A3", 14), (42, "C4", 14), (50, "D4", 14), (58, "B3", 14),
    ], default_sfx=14)
    set_octave_bass(43, ["E", "E", "G", "A", "E", "E", "B", "A", "D", "D", "F", "G", "A", "B", "G", "E"])

    # --- Track 7: Victory / Stage Clear Fanfare (Patterns 44..47) ---
    set_melody(44, [
        (0, "C4", 16), (4, "E4", 16), (8, "G4", 12), (14, "C5", 12),
        (24, "B4", 16), (28, "C5", 12), (36, "D5", 16), (40, "E5", 12), (52, "G5", 12),
    ])
    set_melody(45, [
        (0, "F5", 12), (6, "E5", 16), (12, "D5", 12), (18, "C5", 12),
        (24, "B4", 16), (28, "C5", 12), (36, "G4", 12), (44, "C5", 12), (54, "E5", 12),
    ])
    set_melody(46, [
        (0, "E4", 14), (8, "G4", 14), (14, "E4", 14), (28, "G4", 14),
        (40, "G4", 14), (52, "B4", 14),
    ], default_sfx=14)
    set_octave_bass(47, ["C", "C", "E", "G", "F", "F", "A", "F", "G", "G", "B", "G", "C", "C", "G", "C"])

    tracks = bytearray(8 * 51)

    def pat_code(p):
        # TIC-80 track pattern slots reserve 0 for empty/mute and store patterns as 1..60 (pat_idx + 1).
        return 0 if p is None or p < 0 else ((p + 1) & 0x3F)

    def write_track(t_idx, frame_list, tempo_delta=0, speed_delta=-1):
        base = t_idx * 51
        for f_idx, (p0, p1, p2, p3) in enumerate(frame_list):
            val = (
                pat_code(p0)
                | (pat_code(p1) << 6)
                | (pat_code(p2) << 12)
                | (pat_code(p3) << 18)
            )
            tracks[base + f_idx * 3 + 0] = val & 0xFF
            tracks[base + f_idx * 3 + 1] = (val >> 8) & 0xFF
            tracks[base + f_idx * 3 + 2] = (val >> 16) & 0xFF
        tracks[base + 48] = tempo_delta & 0xFF
        tracks[base + 49] = 0
        tracks[base + 50] = speed_delta & 0xFF

    write_track(0, [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 9, 10, 11)], tempo_delta=4, speed_delta=-1)
    write_track(1, [(13, 17, 18, 11), (14, 17, 18, 11), (15, 17, 18, 11), (16, 17, 18, 11)], tempo_delta=10, speed_delta=-1)
    write_track(2, [(19, 23, 25, 11), (20, 23, 25, 11), (21, 23, 25, 11), (22, 24, 25, 11)], tempo_delta=14, speed_delta=-1)
    write_track(3, [(26, 29, 30, 11), (27, 29, 30, 11), (28, 29, 30, 11), (27, 29, 30, 11)], tempo_delta=12, speed_delta=-1)
    write_track(4, [(31, 34, 35, 36), (32, 34, 35, 36), (33, 34, 35, 36), (32, 34, 35, 36)], tempo_delta=16, speed_delta=-2)
    write_track(5, [(37, 39, 35, 36), (38, 39, 35, 36)], tempo_delta=28, speed_delta=-2)
    write_track(6, [(40, 42, 43, 11), (41, 42, 43, 11)], tempo_delta=18, speed_delta=-2)
    write_track(7, [(44, 46, 47, 11), (45, 46, 47, 11)], tempo_delta=6, speed_delta=-1)

    return bytes(patterns), bytes(tracks)


LUA_CODE = r"""-- title:  SF2' CHAMPION EDITION 80
-- author: SF2' CE NGPC Tribute
-- desc:   Street Fighter II': Champion Edition (NGPC Chibi Style)
-- version: __GAME_VERSION__
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
"""

LUA_CODE = LUA_CODE.replace("__GAME_VERSION__", VERSION)


def _minify_lua_line(line: str) -> str:
    """Collapse redundant spaces/tabs outside string literals without altering Lua token boundaries."""
    punct = set("=,+*/%^#<>~(){}[];:,")
    res = []
    in_q = None
    esc = False
    n = len(line)
    i = 0
    while i < n:
        ch = line[i]
        if in_q:
            res.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_q = ch
            res.append(ch)
            i += 1
            continue
        if ch in (" ", "\t"):
            while i + 1 < n and line[i + 1] in (" ", "\t"):
                i += 1
            prev = res[-1] if res else ""
            nxt = line[i + 1] if i + 1 < n else ""
            if not prev or not nxt:
                i += 1
                continue
            # Keep space if removing it could merge adjacent identifiers/numbers or form "--"
            if (prev == "-" and nxt == "-") or (prev in punct) or (nxt in punct):
                if prev in punct or nxt in punct:
                    i += 1
                    continue
            if prev == "-" and nxt != "-":
                i += 1
                continue
            if nxt == "-" and prev != "-":
                i += 1
                continue
            res.append(" ")
            i += 1
            continue
        res.append(ch)
        i += 1
    return "".join(res)


def compact_lua_for_tic(src: str) -> str:
    """Strip comments, compact redundant whitespace, and alias long internal helpers outside strings so CHUNK_CODE stays comfortably under TIC-80's 65535-byte limit."""
    headers = []
    out = []
    for raw in src.splitlines():
        st = raw.strip()
        if not st:
            continue
        if st.startswith("--"):
            if any(st.startswith(k) for k in ("-- title:", "-- author:", "-- desc:", "-- version:", "-- script:")):
                headers.append(st)
            continue
        # Strip inline -- comments only when outside quoted strings
        in_q = None
        esc = False
        cut = None
        for idx in range(len(st) - 1):
            ch = st[idx]
            if esc:
                esc = False
                continue
            if in_q:
                if ch == "\\":
                    esc = True
                elif ch == in_q:
                    in_q = None
                continue
            if ch in ('"', "'"):
                in_q = ch
            elif ch == "-" and st[idx + 1] == "-":
                cut = idx
                break
        if cut is not None:
            st = st[:cut].rstrip()
        if st:
            out.append(_minify_lua_line(st))
    body = "\n".join(out)
    aliases = {
        "draw_chibi_head": "_dh",
        "draw_chibi_spr": "_ds",
        "check_special_cmd": "_cs",
        "get_atk_trigger": "_ga",
        "resolve_collisions": "_rc",
        "update_fighter": "_uf",
        "push_input_hist": "_pi",
        "dither_seam": "_dm",
        "set_char_pal": "_cp",
        "pal_remap": "_pm",
        "pal_reset": "_pr",
        "out_rect": "_or",
        "out_circ": "_oc",
        "draw_fight_hud": "_fh",
        "update_car_bonus": "_ub",
        "draw_car_bonus": "_db",
        "start_car_bonus": "_sc",
        "make_fighter": "_mf",
        "make_normal": "_mn",
        "resolve_hit": "_rh",
        "spawn_proj": "_sp",
        "spawn_popup": "_su",
        "spawn_fx": "_sx",
        "add_shake": "_as",
        "try_throw": "_tt",
        "is_kick": "_ik",
        "draw_stage": "_dg",
        "draw_fighter": "_df",
        "draw_title": "_dt",
        "update_title": "_ut",
        "draw_select": "_dl",
        "update_select": "_ul",
        "draw_vs": "_dv",
        "draw_guide": "_du",
        "update_guide": "_uu",
        "draw_win": "_dw",
        "step_fight": "_sf",
        "draw_fight": "_dr",
        "read_all_inputs": "_ri",
        "any_p1_press": "_ap",
        "human_any_btn": "_hb",
        "get_rel_dir": "_gd",
        "match_seq": "_ms",
        "has_360": "_h3",
        "sync_music": "_sm",
        "sfx_play": "_xp",
        "init_stage": "_is",
        "start_round": "_sr",
        "start_match": "_mt",
        "run_ai": "_ra",
        "draw_flag": "_fl",
        "round_over_t": "_ro",
        "ko_echo_t": "_ke",
        "start_special": "_ss",
        "p2_cursor": "_c2",
        "title_idle": "_ti",
        "match_banner_t": "_bt",
        "btn_idx": "_bi",
        "FLOOR_Y": "_fy",
        "game_mode": "_gm",
        "p1_score": "_s1",
        "reach": "_rc2",
        "match_banner": "_mb",
        "p1_cursor": "_c1",
        "facing": "_fc",
        "title_cursor": "_tc",
        "hitstop": "_hs",
        "is_attract": "_ia",
        "freeze_t": "_ft",
        "guide_page": "_gp",
        "atk_btn": "_ab",
        "FS_ATTACK": "_fa",
        "p1_pick": "_k1",
        "p2_pick": "_k2",
        "arcade_order": "_ao",
        "startup": "_su2",
        "ST_TITLE": "_st0",
        "timer_sec": "_ts",
        "FS_DIZZY": "_fd",
        "arcade_idx": "_ai",
        "chg_b_keep": "_cbk",
        "FS_IDLE": "_fi",
        "FS_CROUCH": "_fcr",
        "country": "_ct",
        "combo_cnt": "_cc",
        "combo_show_t": "_cst",
        "FS_BLOCK_C": "_fbc",
        "chg_d_keep": "_cdk",
        "cur_track": "_ctr",
        "p1_ready": "_r1",
        "throw_invuln": "_thi",
        "STG_W": "_sw",
        "shake_amp": "_sa",
        "buf_btn_t": "_bbt",
        "p2_ready": "_r2",
        "cam_x": "_cx",
        "proj_invuln": "_pi2",
        "show_hitboxes": "_shb",
        "first_hit_done": "_fhd",
        "blockstun_t": "_bst",
        "hitstun_t": "_hst",
        "timer_sub": "_tsb",
        "attract_t": "_att",
        "sfx_muted": "_smu",
        "prev_state": "_ps",
    }
    alias_re = re.compile(r"\b(" + "|".join(aliases.keys()) + r")\b")
    # Preserve double-quoted string literals verbatim while shortening internal identifiers in code body only
    parts = re.split(r'("(?:\\.|[^"\\])*")', body)
    for idx in range(0, len(parts), 2):
        parts[idx] = alias_re.sub(lambda m: aliases[m.group(0)], parts[idx])
    compacted_body = "".join(parts)
    if headers:
        return "\n".join(headers) + "\n" + compacted_body
    return compacted_body


def format_tag_section(tag, raw_bytes, count, item_size, flip=True):
    lines = [f"-- <{tag}>"]
    for i in range(count):
        chunk = raw_bytes[i * item_size : (i + 1) * item_size]
        if any(chunk):
            lines.append(f"-- {i:03d}:{buf_to_tic_str(chunk, flip=flip)}")
    lines.append(f"-- </{tag}>")
    return "\n".join(lines)


def build_cartridges(out_dir="."):
    tiles_bin = assemble_tile_bank()

    waves_bin = build_waveforms()
    sfx_bin = build_sfx_samples()
    patterns_bin, tracks_bin = build_music()
    pal_bin = bytes(b for rgb in NGPC_SF2_16 for b in rgb)

    sections = [
        LUA_CODE.strip(),
        format_tag_section("TILES", tiles_bin, 256, 32, flip=True),
        format_tag_section("WAVES", waves_bin, 16, 16, flip=True),
        format_tag_section("SFX", sfx_bin, 64, 66, flip=True),
        format_tag_section("PATTERNS", patterns_bin, 60, 192, flip=True),
        format_tag_section("TRACKS", tracks_bin, 8, 51, flip=True),
        format_tag_section("PALETTE", pal_bin, 1, 48, flip=False),
    ]
    full_lua = "\n\n".join(sections) + "\n"

    lua_path = os.path.join(out_dir, "sf2_ce_80.lua")
    with open(lua_path, "w", encoding="utf-8") as f:
        f.write(full_lua)

    def make_chunk(chunk_type, data, bank=0):
        header_byte = ((bank & 0x7) << 5) | (chunk_type & 0x1F)
        size = len(data)
        return struct.pack("<BHB", header_byte, size, 0) + data

    compact_code = compact_lua_for_tic(LUA_CODE.strip())
    code_bytes = compact_code.encode("utf-8")
    if len(code_bytes) > 65535:
        raise ValueError(f"Lua cartridge exceeds 65535-byte code chunk budget ({len(code_bytes)} bytes)")

    tic_bin = bytearray()
    tic_bin += make_chunk(17, b"")
    tic_bin += make_chunk(12, pal_bin)
    tic_bin += make_chunk(1, tiles_bin)
    tic_bin += make_chunk(10, waves_bin)
    tic_bin += make_chunk(9, sfx_bin[: 20 * 66])
    tic_bin += make_chunk(15, patterns_bin[: 48 * 192])
    tic_bin += make_chunk(14, tracks_bin[: 8 * 51])
    tic_bin += make_chunk(5, code_bytes)

    tic_path = os.path.join(out_dir, "sf2_ce_80.tic")
    with open(tic_path, "wb") as f:
        f.write(tic_bin)

    print(
        f"Built v{VERSION} sf2_ce_80.lua ({len(full_lua)} bytes) & sf2_ce_80.tic ({len(tic_bin)} bytes, code={len(code_bytes)}B)"
    )
    return full_lua, bytes(tic_bin)


if __name__ == "__main__":
    import sys

    build_cartridges(sys.argv[1] if len(sys.argv) > 1 else ".")
