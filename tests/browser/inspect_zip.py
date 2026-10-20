"""Read-only inventory for the synthetic browser ZIP download."""

from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

_MAX_TEST_ARCHIVE_BYTES = 10 * 1024 * 1024


def main() -> None:
    """Report archive member names and digests without extracting files."""
    if len(sys.argv) != 2:
        raise SystemExit("Expected one downloaded ZIP path.")
    with ZipFile(Path(sys.argv[1])) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if (
            len(names) != len(set(names))
            or any(info.is_dir() for info in infos)
            or sum(info.file_size for info in infos) > _MAX_TEST_ARCHIVE_BYTES
            or archive.testzip() is not None
        ):
            raise ValueError("Invalid synthetic site ZIP.")
        digests = {info.filename: sha256(archive.read(info)).hexdigest() for info in infos}
    sys.stdout.write(json.dumps({"names": sorted(names), "sha256": digests}, sort_keys=True))


if __name__ == "__main__":
    main()
