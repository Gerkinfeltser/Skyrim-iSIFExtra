"""
sif_icon_builder.py - Generate SIF-compatible icon SWFs from PNG images.

Takes PNG files and produces minimal SWFs with ExportAssets that Status
Indicator Framework (SIF) can load via GetResource/AttachMovie. Bitmaps
are encoded as DefineBitsLossless2 (tag 36) — Scaleform does not support
JPEG3 (tag 35). Static icons only; animated multi-frame icons require
Flash CS6 or manual SWF assembly.

Requirements:
    pip install Pillow (everything else is stdlib)

Usage:
    python sif_icon_builder.py icon.png -n myIcon
    python sif_icon_builder.py icon.png -n myIcon -r 32 -o icons.swf
    python sif_icon_builder.py icon1.png icon2.png -n icon1,icon2 -o pack.swf

Options:
    -n  Export name(s), comma-separated (must match SIF JSON "label" field)
    -r  Resize longest side to N pixels, keep aspect ratio
    -c  Tint color as hex (e.g. FF0000), multiplied onto image preserving alpha
    -o  Output SWF file path
    -s  Stage size in pixels (default: 64, does not affect icon size)
    --fps  Frame rate (default: 30)
"""

__version__ = "1.0.0"

import argparse
import struct
import zlib
import io
from pathlib import Path
from PIL import Image


TWIPS_PER_PIXEL = 20


class BitWriter:
    def __init__(self):
        self.bytes = bytearray()
        self.current_byte = 0
        self.bit_pos = 7

    def write_ub(self, value, num_bits):
        for i in range(num_bits - 1, -1, -1):
            bit = (value >> i) & 1
            self.current_byte |= (bit << self.bit_pos)
            self.bit_pos -= 1
            if self.bit_pos < 0:
                self.bytes.append(self.current_byte)
                self.current_byte = 0
                self.bit_pos = 7

    def write_sb(self, value, num_bits):
        if value < 0:
            self.write_ub(value & ((1 << num_bits) - 1), num_bits)
        else:
            self.write_ub(value, num_bits)

    def byte_align(self):
        if self.bit_pos < 7:
            self.bytes.append(self.current_byte)
            self.current_byte = 0
            self.bit_pos = 7

    def flush(self):
        self.byte_align()
        return bytes(self.bytes)


def _sb_nbits(*values):
    mx = max(abs(v) for v in values)
    if mx == 0:
        return 1
    return mx.bit_length() + 1


def make_rect(xmin, xmax, ymin, ymax):
    bw = BitWriter()
    nbits = _sb_nbits(xmin, xmax, ymin, ymax)
    bw.write_ub(nbits, 5)
    bw.write_sb(xmin, nbits)
    bw.write_sb(xmax, nbits)
    bw.write_sb(ymin, nbits)
    bw.write_sb(ymax, nbits)
    bw.byte_align()
    return bw.flush()


def make_matrix_bytealigned(has_scale=False, scale_x=1.0, scale_y=1.0,
                            translate_x=0, translate_y=0):
    bw = BitWriter()
    if has_scale:
        sx_fixed = int(scale_x * 65536)
        sy_fixed = int(scale_y * 65536)
        snbits = _sb_nbits(sx_fixed, sy_fixed)
        bw.write_ub(1, 1)
        bw.write_ub(snbits, 5)
        bw.write_sb(sx_fixed, snbits)
        bw.write_sb(sy_fixed, snbits)
    else:
        bw.write_ub(0, 1)

    bw.write_ub(0, 1)

    if translate_x != 0 or translate_y != 0:
        tnbits = _sb_nbits(translate_x, translate_y)
        bw.write_ub(tnbits, 5)
        bw.write_sb(translate_x, tnbits)
        bw.write_sb(translate_y, tnbits)
    else:
        bw.write_ub(0, 5)

    bw.byte_align()
    return bw.flush()


def make_swf_tag(tag_type, data):
    length = len(data)
    if length < 0x3F:
        return struct.pack('<H', (tag_type << 6) | length) + data
    else:
        return struct.pack('<H', (tag_type << 6) | 0x3F) + struct.pack('<I', length) + data


def make_file_attributes():
    return make_swf_tag(69, b'\x00\x00\x00\x00')


def make_set_background_color(r=0xFF, g=0xFF, b=0xFF):
    return make_swf_tag(9, bytes([r, g, b]))


def make_define_bits_lossless2(chid, image):
    img = image.convert('RGBA') if image.mode != 'RGBA' else image
    w, h = img.size
    pixels = img.load()

    raw_data = bytearray(w * h * 4)
    idx = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            raw_data[idx] = a
            raw_data[idx + 1] = r
            raw_data[idx + 2] = g
            raw_data[idx + 3] = b
            idx += 4

    compressed = zlib.compress(bytes(raw_data))
    header = struct.pack('<HBHH', chid, 5, w, h)
    return make_swf_tag(36, header + compressed)


def make_define_shape2(shape_chid, bitmap_chid, width, height):
    half_w = width * TWIPS_PER_PIXEL // 2
    half_h = height * TWIPS_PER_PIXEL // 2

    buf = bytearray()

    buf += struct.pack('<H', shape_chid)
    buf += make_rect(-half_w, half_w, -half_h, half_h)

    buf.append(1)
    buf.append(0x41)
    buf += struct.pack('<H', bitmap_chid)

    scale = float(TWIPS_PER_PIXEL)
    tx = -(width * TWIPS_PER_PIXEL // 2)
    ty = -(height * TWIPS_PER_PIXEL // 2)
    buf += make_matrix_bytealigned(has_scale=True, scale_x=scale, scale_y=scale,
                                   translate_x=tx, translate_y=ty)

    buf.append(0)

    bw = BitWriter()
    bw.write_ub(1, 4)
    bw.write_ub(0, 4)

    bw.write_ub(0, 1)
    bw.write_ub(0, 1)
    bw.write_ub(0, 1)
    bw.write_ub(1, 1)
    bw.write_ub(0, 1)
    bw.write_ub(1, 1)

    move_nbits = _sb_nbits(-half_w, -half_h)
    bw.write_ub(move_nbits, 5)
    bw.write_sb(-half_w, move_nbits)
    bw.write_sb(-half_h, move_nbits)
    bw.write_ub(1, 1)

    dx = half_w * 2
    dy = half_h * 2
    edge_nbits = _sb_nbits(dx, -dx, dy, -dy)
    if edge_nbits < 2:
        edge_nbits = 2
    en = edge_nbits - 2

    for delta, is_vert in [(dx, False), (dy, True), (-dx, False), (-dy, True)]:
        bw.write_ub(1, 1)
        bw.write_ub(1, 1)
        bw.write_ub(en, 4)
        bw.write_ub(0, 1)
        bw.write_ub(1 if is_vert else 0, 1)
        bw.write_sb(delta, edge_nbits)

    bw.write_ub(0, 1)
    bw.write_ub(0, 5)

    buf += bw.flush()

    return make_swf_tag(22, bytes(buf))


def make_define_sprite(sprite_chid, shape_chid):
    sprite_body = io.BytesIO()
    sprite_body.write(struct.pack('<HH', sprite_chid, 1))

    place_buf = bytearray()
    place_buf.append(0x06)
    place_buf += struct.pack('<H', 1)
    place_buf += struct.pack('<H', shape_chid)
    place_buf += make_matrix_bytealigned()

    sprite_body.write(make_swf_tag(26, bytes(place_buf)))
    sprite_body.write(make_swf_tag(12, b'\x07\x00'))
    sprite_body.write(make_swf_tag(1, b''))

    return make_swf_tag(39, sprite_body.getvalue())


def make_export_assets(export_name, sprite_chid):
    data = struct.pack('<HH', 1, sprite_chid)
    data += export_name.encode('ascii') + b'\x00'
    return make_swf_tag(56, data)


def build_sif_swf(icons, stage_size=64, fps=30, swf_version=8):
    stage_twips = stage_size * TWIPS_PER_PIXEL

    tags = io.BytesIO()
    tags.write(make_file_attributes())
    tags.write(make_set_background_color())

    next_chid = 1

    for name, img in icons:
        w, h = img.size
        bitmap_chid = next_chid; next_chid += 1
        shape_chid = next_chid; next_chid += 1
        sprite_chid = next_chid; next_chid += 1

        tags.write(make_define_bits_lossless2(bitmap_chid, img))
        tags.write(make_define_shape2(shape_chid, bitmap_chid, w, h))
        tags.write(make_define_sprite(sprite_chid, shape_chid))
        tags.write(make_export_assets(name, sprite_chid))

    tags.write(make_swf_tag(1, b''))
    tags.write(make_swf_tag(0, b''))

    tag_data = tags.getvalue()

    header = io.BytesIO()
    header.write(make_rect(0, stage_twips, 0, stage_twips))
    header.write(struct.pack('<H', fps << 8))
    header.write(struct.pack('<H', 1))

    body = header.getvalue() + tag_data

    swf = io.BytesIO()
    swf.write(b'FWS')
    swf.write(struct.pack('B', swf_version))
    swf.write(struct.pack('<I', 8 + len(body)))
    swf.write(body)

    return swf.getvalue()


def main():
    parser = argparse.ArgumentParser(description='Build SIF-compatible icon SWFs from PNG images')
    parser.add_argument('inputs', nargs='+', help='Input PNG file(s)')
    parser.add_argument('-n', '--names', help='Export name(s), comma-separated')
    parser.add_argument('-o', '--output', help='Output SWF file')
    parser.add_argument('-c', '--color', help='Tint color as hex (e.g. FF0000) multiplied onto image')
    parser.add_argument('-r', '--resize', type=int, default=0,
                        help='Scale longest side to N pixels, keep aspect ratio')
    parser.add_argument('-s', '--stage', type=int, default=64, help='Stage size in pixels (default: 64)')
    parser.add_argument('--fps', type=int, default=30, help='Frame rate (default: 30)')

    args = parser.parse_args()

    icons = []
    for i, path in enumerate(args.inputs):
        img = Image.open(path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        if args.resize > 0:
            w, h = img.size
            longest = max(w, h)
            if longest != args.resize:
                ratio = args.resize / longest
                new_w = max(1, round(w * ratio))
                new_h = max(1, round(h * ratio))
                img = img.resize((new_w, new_h), Image.LANCZOS)

        if args.color:
            tint = tuple(int(args.color.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            pixels = img.load()
            w, h = img.size
            for y in range(h):
                for x in range(w):
                    r, g, b, a = pixels[x, y]
                    pixels[x, y] = (int(r * tint[0]), int(g * tint[1]), int(b * tint[2]), a)

        if args.names:
            names = [n.strip() for n in args.names.split(',')]
            name = names[i] if i < len(names) else Path(path).stem
        else:
            name = Path(path).stem

        icons.append((name, img))
        print(f'  {name}: {img.size[0]}x{img.size[1]} from {path}')

    swf_data = build_sif_swf(icons, stage_size=args.stage, fps=args.fps)

    output = args.output
    if not output:
        output = str(Path(args.inputs[0]).with_suffix('.swf'))

    with open(output, 'wb') as f:
        f.write(swf_data)

    print(f'  -> {output} ({len(swf_data)} bytes, {len(icons)} icon(s))')


if __name__ == '__main__':
    main()
