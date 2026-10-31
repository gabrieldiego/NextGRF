"""Small dependency-free PDF writer: vector text and lossless sprite images."""
import textwrap
import zlib


def escaped(value):
    return str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


class PDF:
    width, height = 595, 842

    def __init__(self, title='NextGRF - Default and Extended Aircraft Catalog', category='Aircraft'):
        self.title = title
        self.category = category
        self.objects = [None]
        self.pages = []
        self.regular = self.add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>')
        self.bold = self.add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>')
        self.mono = self.add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>')
        self.page_tree = self.add(b'')

    def add(self, data):
        self.objects.append(data)
        return len(self.objects)-1

    def stream(self, data, extra=''):
        compressed = zlib.compress(data, 9)
        return self.add(f'<< /Length {len(compressed)} /Filter /FlateDecode {extra} >>\nstream\n'.encode() + compressed + b'\nendstream')

    def page(self):
        self.commands = []
        self.images = {}

    def rect(self, x, y, w, h, color):
        self.commands.append(f'{color[0]} {color[1]} {color[2]} rg {x} {self.height-y-h} {w} {h} re f')

    def text(self, x, y, value, size=10, bold=False, color=(.12,.17,.23), mono=False):
        font = 'FM' if mono else 'FB' if bold else 'FR'
        self.commands.append(f'BT /{font} {size} Tf {color[0]} {color[1]} {color[2]} rg 1 0 0 1 {x} {self.height-y} Tm ({escaped(value)}) Tj ET')

    def paragraph(self, x, y, value, width=93, size=10, leading=15):
        for line in textwrap.wrap(value, width=width):
            self.text(x, y, line, size)
            y += leading
        return y

    def image(self, image, x, y, width, height):
        rgb = image.convert('RGBA')
        from PIL import Image
        background = Image.new('RGBA', rgb.size, (239, 243, 247, 255))
        background.alpha_composite(rgb)
        rgb = background.convert('RGB')
        identifier = self.stream(rgb.tobytes(), f'/Type /XObject /Subtype /Image /Width {rgb.width} /Height {rgb.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Interpolate false')
        name = f'I{len(self.images)}'
        self.images[name] = identifier
        self.commands.append(f'q {width} 0 0 {height} {x} {self.height-y-height} cm /{name} Do Q')

    def end_page(self):
        self.text(36, 816, f'NextGRF | {self.category} catalog | DEFAULT and NEXTGRF clearly identified', 8, color=(.40,.44,.50))
        self.text(536, 816, str(len(self.pages)+1), 8)
        content = self.stream('\n'.join(self.commands).encode('cp1252', 'replace'))
        images = ' '.join(f'/{name} {identifier} 0 R' for name, identifier in self.images.items())
        self.pages.append(self.add(f'<< /Type /Page /Parent {self.page_tree} 0 R /MediaBox [0 0 {self.width} {self.height}] /Resources << /Font << /FR {self.regular} 0 R /FB {self.bold} 0 R /FM {self.mono} 0 R >> /XObject << {images} >> >> /Contents {content} 0 R >>'.encode()))

    def save(self, path):
        self.objects[self.page_tree] = f'<< /Type /Pages /Count {len(self.pages)} /Kids [{" ".join(f"{p} 0 R" for p in self.pages)}] >>'.encode()
        catalog = self.add(f'<< /Type /Catalog /Pages {self.page_tree} 0 R >>'.encode())
        info = self.add(f'<< /Title ({escaped(self.title)}) /Author (NextGRF project) /Subject (Vehicle properties and eight directional sprites) >>'.encode('cp1252', 'replace'))
        output = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = [0]
        for index, obj in enumerate(self.objects[1:], 1):
            offsets.append(len(output))
            output.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
        xref = len(output)
        output.extend(f'xref\n0 {len(self.objects)}\n0000000000 65535 f \n'.encode())
        for offset in offsets[1:]:
            output.extend(f'{offset:010d} 00000 n \n'.encode())
        output.extend(f'trailer\n<< /Size {len(self.objects)} /Root {catalog} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
        path.write_bytes(output)
