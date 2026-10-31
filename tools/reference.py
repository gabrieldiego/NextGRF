"""Fetch the pinned, checksum-verified OpenGFX2 Classic reference release."""
import hashlib
from pathlib import Path
import tarfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.8.1'
NAME = f'OpenGFX2_Classic-{VERSION}.tar'
URL = f'https://github.com/OpenTTD/OpenGFX2/releases/download/{VERSION}/{NAME}'
SHA256 = '2f4d0d8cd82b9b15d7c5a742581bfd11a08d4fd54fc0743f1f8a1032e3b5eeaf'


def ensure_reference():
    destination = ROOT/'build/reference'
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination/NAME
    if not archive.exists():
        for attempt in range(3):
            try:
                request = urllib.request.Request(URL, headers={'User-Agent': 'NextGRF-reference-fetcher'})
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read()
                if hashlib.sha256(data).hexdigest() != SHA256:
                    raise ValueError('OpenGFX2 download checksum mismatch')
                archive.write_bytes(data)
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(1)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError(f'OpenGFX2 reference checksum mismatch: {archive}')
    with tarfile.open(archive) as bundle:
        bundle.extractall(destination, filter='data')
    return next(destination.glob('*/opengfx2_8.obg')).parent


if __name__ == '__main__':
    print(ensure_reference())
