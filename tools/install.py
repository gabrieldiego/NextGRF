"""Install NextGRF and its reference base set in the current user's data profile."""
import argparse
import hashlib
import json
import os
import errno
from pathlib import Path
import shutil
import tempfile

from reference import NAME, ROOT, ensure_reference


def install_file(source, destination):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == digest:
        return dict(path=str(destination), sha256=digest, action='already installed')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        # Preserve any earlier package outside the game's scanning directory.
        backups = ROOT/'build/profile-backups'
        backups.mkdir(exist_ok=True)
        old_hash = hashlib.sha256(destination.read_bytes()).hexdigest()[:12]
        shutil.copy2(destination, backups/f'{destination.name}.{old_hash}.bak')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(source.read_bytes())
        temporary.chmod(0o644)
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f'Installed file verification failed: {destination}')
    return dict(path=str(destination), sha256=digest, action='installed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'openttd'
    parser.add_argument('--profile', type=Path, default=default)
    args = parser.parse_args()
    ensure_reference()
    records = []
    for source, destination in [
        (ROOT/'build/reference'/NAME, args.profile/'baseset'/NAME),
        (ROOT/'build/nextgrf.tar', args.profile/'newgrf/nextgrf.tar'),
    ]:
        record = install_file(source, destination)
        records.append(record)
        print(record['action'] + ': ' + record['path'])
    receipt = ROOT/'build/install-receipt.json' if args.profile == default else args.profile/'nextgrf-install-receipt.json'
    receipt.write_text(json.dumps(records, indent=2)+'\n')
    print('Restart/rescan OpenTTD, select OpenGFX2 Classic, and add NextGRF before starting a new game.')


if __name__ == '__main__':
    try:
        main()
    except OSError as error:
        if error.errno in (errno.EROFS, errno.EACCES, errno.EPERM):
            raise SystemExit('Profile installation is blocked by filesystem permissions. '
                             'No game configuration was changed. Run this installer from '
                             'your normal desktop terminal, where the profile is writable. '
                             f'Detail: {error}') from None
        raise
