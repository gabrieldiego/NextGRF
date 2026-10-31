"""Render original aircraft meshes to DOS-palette sprites, with company colours.

Coordinates are aircraft-local: X is starboard, negative Y is the nose, Z is up.
The orthographic camera, light and ground anchor stay fixed for all eight headings.
Playable artwork is generated from the editable meshes below.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw
from nml.palette import raw_palette_data

CELL = (96, 96)
PALETTE = raw_palette_data[0]


def canvas(size):
    image = Image.new("P", size, 0)
    image.putpalette(PALETTE)
    image.info["transparency"] = 0
    return image


def mesh(plane):
    faces = []
    shape = plane["shape"]
    length = plane["length"]
    width = 0.065 if shape not in ("doubledeck", "freighter") else 0.10
    if shape in ("biplane", "cabin_biplane"):
        width = 0.07

    def face(points, material="silver"):
        faces.append(([(x * length, y * length, z * length) for x, y, z in points], material))

    def slab(points, z, material="wing", thickness=0.018):
        face([(x, y, z) for x, y in points], material)
        face([(x, y, z - thickness) for x, y in reversed(points)], material)
        for a, b in zip(points, points[1:] + points[:1]):
            face([(a[0], a[1], z), (a[0], a[1], z - thickness),
                  (b[0], b[1], z - thickness), (b[0], b[1], z)], material)

    def body(x, y, z, half_length, radius, material="silver"):
        stations = [(-1, .03), (-.88, .58), (-.68, .93), (-.3, 1),
                    (.25, 1), (.65, .74), (.92, .25), (1, .015)]
        rings = [[(x + radius * r * math.cos(t * math.tau / 12), y + q * half_length,
                   z + radius * r * math.sin(t * math.tau / 12)) for t in range(12)]
                 for q, r in stations]
        for first, second in zip(rings, rings[1:]):
            for j in range(12):
                mat = "cc" if material == "silver" and j in (0, 5) else material
                face([first[j], second[j], second[(j + 1) % 12], first[(j + 1) % 12]], mat)

    # Distinct wing plans are editable here, rather than independent rotated drawings.
    straight = shape in ("biplane", "cabin_biplane", "trimotor", "piston", "turboprop",
                         "long_turboprop", "high_turboprop", "electric", "regional_quad", "freighter")
    span = .62 if straight else .55
    if shape in ("longwing", "blended", "joined"):
        span = .70
    if shape == "delta":
        span = .34
    wing_z = .19 if shape in ("high_turboprop", "electric", "regional_quad", "freighter", "trimotor") else .12
    for sign in (-1, 1):
        if straight:
            wing = [(sign * .035, -.08), (sign * span, -.035), (sign * span, .09), (sign * .035, .16)]
        elif shape == "delta":
            wing = [(sign * .025, -.31), (sign * span, .30), (sign * .08, .32)]
        elif shape == "blended":
            wing = [(0, -.43), (sign * .19, -.18), (sign * span, .18),
                    (sign * .65, .28), (sign * .12, .35), (0, .28)]
        else:
            wing = [(sign * .045, -.18), (sign * span, .11),
                    (sign * span, .18), (sign * .045, .07)]
        slab(wing, wing_z, "wood" if shape in ("biplane", "cabin_biplane") else "wing")
        if shape in ("biplane", "cabin_biplane"):
            slab(wing, .32, "wood")
            for xx in (.24, .48):
                face([(sign * xx, -.025, .12), (sign * xx, -.025, .32),
                      (sign * (xx + .012), -.025, .32), (sign * (xx + .012), -.025, .12)], "dark")
        if shape in ("winglet_jet", "longwing", "doubledeck"):
            face([(sign * span, .11, wing_z), (sign * span, .18, wing_z),
                  (sign * (span + .025), .19, wing_z + .12),
                  (sign * (span + .025), .14, wing_z + .12)], "cc")
        if shape == "joined":
            slab([(sign * .05, .37), (sign * span, .17),
                  (sign * span, .11), (sign * .05, .24)], .20, "cc")
        if shape not in ("delta", "blended"):
            tail_z = .31 if shape in ("rearjet", "high_turboprop", "regional_quad") else .15
            slab([(sign * .025, .28), (sign * .23, .38),
                  (sign * .23, .45), (sign * .025, .41)], tail_z, "wing")
        if shape in ("canard", "joined"):
            slab([(sign * .035, -.34), (sign * .20, -.26),
                  (sign * .20, -.20), (sign * .035, -.25)], .19, "cc")

    body(0, 0, .16, .50, width, "wood" if shape == "biplane" else "silver")
    # Cockpit glazing follows the fuselage, and passenger windows are real geometry.
    face([(-width * .78, -.37, .18), (width * .78, -.37, .18),
          (width * .62, -.30, .16 + width), (-width * .62, -.30, .16 + width)], "glass")
    if shape == "biplane":
        slab([(-.035, -.12), (.035, -.12), (.035, -.02), (-.035, -.02)], .23, "dark")
    else:
        for sign in (-1, 1):
            for n in range(max(3, int(length / 3))):
                yy = -.24 + n * .48 / max(3, int(length / 3))
                for zz in ([.18, .23] if shape == "doubledeck" else [.18]):
                    face([(sign * width, yy, zz), (sign * width, yy + .019, zz),
                          (sign * width, yy + .019, zz + .023), (sign * width, yy, zz + .023)], "glass")
    if shape != "blended":
        face([(0, .22, .18), (0, .37, .43), (0, .46, .41), (0, .45, .16)], "cc")
        face([(.009, .22, .18), (.009, .37, .43), (.009, .46, .41), (.009, .45, .16)], "cc")

    prop = shape in ("biplane", "cabin_biplane", "trimotor", "piston", "turboprop",
                     "long_turboprop", "high_turboprop", "electric")
    if shape == "biplane":
        engines = [(0, -.48, .16)]
    elif shape in ("rearjet", "canard", "blended"):
        engines = [(-.12, .25, .18), (.12, .25, .18)]
    else:
        positions = [.23, .42] if shape in ("electric", "regional_quad", "doubledeck") else [.25]
        engines = [(sign * x, -.015 if prop else .025, wing_z - .045)
                   for sign in (-1, 1) for x in positions]
        if shape == "trimotor":
            engines.append((0, -.46, .16))
        if shape == "trijet":
            engines.append((0, .31, .29))
    for x, y, z in engines:
        radius = .026 if prop else .043
        body(x, y, z, .09, radius, "silver")
        face([(x - radius * .7, y - .085, z - radius * .7),
              (x + radius * .7, y - .085, z - radius * .7),
              (x + radius * .7, y - .085, z + radius * .7),
              (x - radius * .7, y - .085, z + radius * .7)], "dark")
        if prop:
            for dx, dz in ((.095, .012), (.012, .095)):
                face([(x - dx, y - .105, z - dz), (x + dx, y - .105, z + dz),
                      (x + dx + .009, y - .105, z + dz), (x - dx + .009, y - .105, z - dz)], "dark")
    return faces


def render(plane, direction, zoom=1):
    angle = direction * math.pi / 4
    ca, sa = math.cos(angle), math.sin(angle)

    def transform(point):
        x, y, z = point
        return (ca * x - sa * y, sa * x + ca * y, z)

    image = canvas((CELL[0] * zoom, CELL[1] * zoom))
    draw = ImageDraw.Draw(image)
    transformed = [(list(map(transform, points)), material) for points, material in mesh(plane)]
    # Far-to-near painter order for orthographic projection (camera toward +Y/+Z).
    transformed.sort(key=lambda f: sum(p[1] + p[2] * .58 for p in f[0]) / len(f[0]))
    for points, material in transformed:
        a, b, c = points[:3]
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        normal = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        norm = math.sqrt(sum(n*n for n in normal)) or 1
        shade = max(0, min(1, .53 + (-normal[0] - normal[1] + abs(normal[2])) / norm * .22))
        ramps = {"silver": list(range(7, 16)), "wing": list(range(6, 15)),
                 "cc": list(range(198, 206)), "wood": list(range(105, 115)),
                 "glass": [16, 17, 18, 154, 155], "dark": [1, 2, 3, 4]}
        ramp = ramps[material]
        color = ramp[round(shade * (len(ramp)-1))]
        pixels = [(round((CELL[0]/2 + x) * zoom), round((CELL[1]/2 + y*.60 - z) * zoom))
                  for x, y, z in points]
        draw.polygon(pixels, fill=color)
    return image


def save_sheet(sheet, path):
    """Preserve unchanged atlas timestamps so NML can reuse its sprite cache."""
    from io import BytesIO
    data = BytesIO()
    sheet.save(data, format='PNG', transparency=0)
    path = Path(path)
    payload = data.getvalue()
    if not path.exists() or path.read_bytes() != payload:
        path.write_bytes(payload)


def write_sheets(planes, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for zoom in (1, 2, 4):
        sheet = canvas((CELL[0] * 8 * zoom, CELL[1] * len(planes) * zoom))
        for row, plane in enumerate(planes):
            for heading in range(8):
                sheet.paste(render(plane, heading, zoom), (heading*CELL[0]*zoom, row*CELL[1]*zoom))
        save_sheet(sheet, directory / f"aircraft-{zoom}x.png")
