"""Read default aircraft properties and original sprites for comparison only.

The GRF v2 reader follows OpenTTD's src/spriteloader/grf.cpp. It supports the
8bpp, normal-zoom reference sprites, including chunked scanlines and LZ77.
"""
import datetime
import configparser
from pathlib import Path
import re
import struct

from PIL import Image
from render import CELL, canvas
from reference import ensure_reference

REPO = Path(__file__).resolve().parents[3]
DEFAULT_GFX = None


class GRF:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        if self.data[:10] != b'\x00\x00GRF\x82\x0d\x0a\x1a\x0a':
            raise ValueError(f'{path}: catalog needs a GRF container v2 file')
        data_offset = struct.unpack_from('<I', self.data, 10)[0]
        self.references = []
        position = 15
        while True:
            size = struct.unpack_from('<I', self.data, position)[0]
            position += 4
            if not size:
                break
            kind = self.data[position]
            position += 1
            self.references.append(struct.unpack_from('<I', self.data, position)[0] if kind == 0xFD else None)
            position += size
        self.sprites = {}
        position = 14 + data_offset
        while True:
            identifier = struct.unpack_from('<I', self.data, position)[0]
            if not identifier:
                break
            size = struct.unpack_from('<I', self.data, position + 4)[0]
            payload = self.data[position + 8:position + 8 + size]
            if payload[0] & 7 == 4 and payload[1] == 0:
                self.sprites[identifier] = payload
            position += 8 + size

    @staticmethod
    def decompress(data, size):
        output = bytearray()
        pos = 0
        while len(output) < size:
            code = data[pos]
            pos += 1
            if code < 128:
                count = code or 128
                output.extend(data[pos:pos+count])
                pos += count
            else:
                count = -((code-256) >> 3)
                offset = ((code & 7) << 8) | data[pos]
                pos += 1
                if not 0 < offset <= len(output):
                    raise ValueError('Invalid sprite back reference')
                for _ in range(count):
                    output.append(output[-offset])
        if len(output) != size:
            raise ValueError('Invalid decompressed sprite length')
        return output

    def image(self, index):
        payload = self.sprites[self.references[index]]
        kind, _, height, width, xoff, yoff = struct.unpack_from('<BBHHhh', payload)
        position = 10
        size = width * height
        if kind & 8:
            size = struct.unpack_from('<I', payload, position)[0]
            position += 4
        pixels = self.decompress(payload[position:], size)
        image = canvas((width, height))
        if kind & 8:
            for y in range(height):
                pos = struct.unpack_from('<I' if size > 65535 else '<H', pixels, y*(4 if size > 65535 else 2))[0]
                while True:
                    if width > 256:
                        length, skip = struct.unpack_from('<HH', pixels, pos)
                        last, length, step = bool(length & 0x8000), length & 0x7fff, 4
                    else:
                        length, skip = pixels[pos:pos+2]
                        last, length, step = bool(length & 128), length & 127, 2
                    pos += step
                    if skip + length > width:
                        raise ValueError('Invalid chunk width')
                    for x in range(length):
                        image.putpixel((skip + x, y), pixels[pos+x])
                    pos += length
                    if last:
                        break
        else:
            image.frombytes(bytes(pixels))
        # Preserve the game anchor, so default and new sprites use the same scale.
        target = canvas(CELL)
        target.paste(image, (CELL[0]//2 + xoff, CELL[1]//2 + yoff))
        return target


def default_aircraft(gfx=DEFAULT_GFX):
    gfx = Path(gfx) if gfx is not None else ensure_reference()
    manifest = configparser.ConfigParser()
    manifest.read(next(gfx.glob('*.obg')))
    source = (REPO / 'src/table/engines.h').read_text()
    info = {}
    for match in re.finditer(r'MA\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),(.*?)//\s*\d+ (.+)', source):
        days, decay, vehicle_life, model_life, climates, name = match.groups()
        date = datetime.date(1920, 1, 1) + datetime.timedelta(days=int(days))
        info[name.strip()] = dict(introduction_date=date.isoformat(), year=date.year,
                                 reliability_decay=int(decay), vehicle_life=int(vehicle_life),
                                 model_life=int(model_life),
                                 climates=['TOYLAND'] if 'T,A,S' not in climates.replace(' ', '') else ['TEMPERATE', 'ARCTIC', 'TROPICAL'])
    table = (REPO / 'src/aircraft_cmd.cpp').read_text().split('static const SpriteID _aircraft_sprite[] = {', 1)[1].split('};', 1)[0]
    image_indices = [int(x, 16) for x in re.findall(r'0x[0-9A-Fa-f]+', table)]
    base = GRF(gfx / manifest['files']['base'])
    toy = GRF(gfx / manifest['files']['toyland'])
    landscape = (REPO / 'src/table/landscape_sprite.h').read_text().split('_landscape_spriteindexes_toyland[] = {', 1)[1].split('};', 1)[0]
    toy_mapping = {}
    offset = 0
    for start, end in re.findall(r'\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)\}', landscape):
        for sprite in range(int(start, 16), int(end, 16)+1):
            toy_mapping[sprite] = offset
            offset += 1
    result = []
    for match in re.finditer(r'AVI\((.*?)\), //\s*(\d+) (.+)', source):
        values, identifier, name = match.groups()
        p = [v.strip() for v in values.split(',')]
        item = dict(info[name.strip()], name=name.strip(), id=int(identifier), source='DEFAULT',
                    passengers=int(p[8]), mail=int(p[7]), cost_factor=int(p[1]),
                    running_cost_factor=int(p[2]), small=p[3] == 'P', helicopter=p[3] == 'H',
                    acceleration=int(p[5]), speed=int(p[6])*128//10 * 1.00584,
                    loading_speed=20, range=0, retire_early=0, cargo_age_period=185,
                    refit_cost=8, sound=p[4], image_index=int(p[0]),
                    refits=['Default aircraft refit mask (varies by climate)'])
        sprites = []
        for direction in range(8):
            sprite_id = image_indices[int(p[0])] + direction
            sprites.append(toy.image(toy_mapping[sprite_id]) if item['climates'] == ['TOYLAND'] else base.image(sprite_id))
        item['sprites'] = sprites
        result.append(item)
    if len(result) != 41:
        raise ValueError(f'Expected 41 default aircraft, read {len(result)}')
    return result
