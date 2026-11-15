#!/usr/bin/env python3
"""Generate crisp NGPC pixel-art PWA icons (192x192, 512x512, 180x180, 32x32 favicon.ico)."""
from pathlib import Path
import struct
import zlib

# NGPC_SF2_16 palette RGBA tuples
PAL = {
    ".": (20, 16, 32, 255),    # 0 Deep Ink
    "W": (244, 244, 248, 255), # 1 Chalk White
    "N": (40, 44, 60, 255),    # 2 Slate Navy
    "S": (78, 88, 114, 255),   # 3 Cool Steel
    "K": (252, 168, 118, 255), # 5 Warm Skin
    "D": (200, 100, 64, 255),  # 6 Shade Skin
    "R": (220, 40, 56, 255),   # 7 Crimson
    "B": (48, 80, 220, 255),   # 8 Cobalt Blue
    "G": (248, 220, 56, 255),  # 9 Champion Gold
    "C": (56, 216, 236, 255),  # 10 Cyan Ki
    "O": (244, 140, 40, 255),  # 14 Tiger Orange
}

# 16x16 pixel-art NGPC Ryu + Champion Gold "80" arcade emblem
GRID_16 = [
    "................",
    ".NNNNNNNNNNNNNN.",
    ".N............N.",
    ".N.GGGG..GGGG.N.",
    ".N.G..G..G..G.N.",
    ".N.RRRRRRRRRR.N.",
    ".N.KKKKKKKKKK.N.",
    ".N.K..KKKK..K.N.",
    ".N.KKKKKKKKKK.N.",
    ".N..KDDDDDDK..N.",
    ".N.WWWW..WWWW.N.",
    ".N.WW.CCCC.WW.N.",
    ".N.W.CCWWCC.W.N.",
    ".N.WWWW..WWWW.N.",
    ".NNNNNNNNNNNNNN.",
    "................",
]


def encode_png(width: int, height: int, rgba_rows: list[bytes]) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw = b"".join(b"\x00" + row for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, level=9))
        + chunk(b"IEND", b"")
    )


def render_icon_png(size: int) -> bytes:
    rows: list[bytes] = []
    for py in range(size):
        gy = (py * 16) // size
        row_src = GRID_16[gy]
        row = bytearray()
        for px in range(size):
            gx = (px * 16) // size
            # Subtle beveled outer frame accent
            if py < size // 32 or py >= size - size // 32 or px < size // 32 or px >= size - size // 32:
                r, g, b, a = PAL["."]
            else:
                r, g, b, a = PAL[row_src[gx]]
            row.extend((r, g, b, a))
        rows.append(bytes(row))
    return encode_png(size, size, rows)


def wrap_png_ico(png_bytes: bytes, size: int = 32) -> bytes:
    header = struct.pack("<HHH", 0, 1, 1)
    dim = 0 if size >= 256 else size
    entry = struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png_bytes), 22)
    return header + entry + png_bytes


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    pub = root / "public"
    pub.mkdir(parents=True, exist_ok=True)
    for filename, size in [
        ("icon-192.png", 192),
        ("icon-512.png", 512),
        ("apple-touch-icon.png", 180),
    ]:
        (pub / filename).write_bytes(render_icon_png(size))
    ico_png = render_icon_png(32)
    (pub / "favicon.ico").write_bytes(wrap_png_ico(ico_png, 32))
    print("Generated pixel-art PWA icons in", pub)


if __name__ == "__main__":
    main()
