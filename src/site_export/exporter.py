"""AURORA P4-001 exclusive folder/ZIP output; cleanup only invocation-owned paths."""

from __future__ import annotations

import stat
from pathlib import Path
from typing import cast
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from src.site_export.models import (
    SiteExportError,
    SiteValidationError,
    StaticSiteBuild,
    _validate_build,  # pyright: ignore[reportPrivateUsage]
)


class StaticSiteExporter:
    """Single-writer exports, not an overwrite API or content-sanitization layer."""

    __slots__ = ()

    def export_folder(self, build: StaticSiteBuild, destination: Path) -> Path:
        """Write exactly the artifact tree to a new explicit directory."""
        files = _validate_build(build)
        destination = _destination(destination)
        owned_files: list[Path] = []
        owned_directories: list[Path] = []
        try:
            destination.mkdir()
            owned_directories.append(destination)
            for item in files:
                path = destination / item.path
                if path.parent != destination and path.parent not in owned_directories:
                    path.parent.mkdir()
                    owned_directories.append(path.parent)
                with path.open("xb") as stream:
                    owned_files.append(path)
                    stream.write(item.data)
        except OSError as error:
            _export_failure(error, owned_files, owned_directories)
        return destination

    def export_zip(self, build: StaticSiteBuild, destination: Path) -> Path:
        """Write a reproducible ZIP_STORED artifact, exclusively and without nesting."""
        files = _validate_build(build)
        destination = _destination(destination)
        owned_files: list[Path] = []
        try:
            with destination.open("xb") as stream:
                owned_files.append(destination)
                with ZipFile(stream, "w", compression=ZIP_STORED) as archive:
                    for item in files:
                        info = ZipInfo(item.path, date_time=(1980, 1, 1, 0, 0, 0))
                        info.create_system = 3
                        info.external_attr = (stat.S_IFREG | 0o644) << 16
                        info.compress_type = ZIP_STORED
                        archive.writestr(info, item.data)
        except OSError as error:
            _export_failure(error, owned_files, [])
        return destination


def _destination(value: object) -> Path:
    if not isinstance(value, Path) or not value.is_absolute():
        raise SiteValidationError("Invalid export destination.")
    path = value
    try:
        for parent in reversed(path.parents):
            try:
                details = parent.lstat()
            except FileNotFoundError:
                raise SiteValidationError("Invalid export destination.") from None
            attributes = cast("int", getattr(details, "st_file_attributes", 0))
            if (
                not stat.S_ISDIR(details.st_mode)
                or stat.S_ISLNK(details.st_mode)
                or attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
            ):
                raise SiteValidationError("Invalid export destination.")
        try:
            path.lstat()
        except FileNotFoundError:
            return path
        raise SiteValidationError("Export destination already exists.")
    except OSError as error:
        raise SiteExportError("Static site export failed.") from error


def _export_failure(error: OSError, files: list[Path], directories: list[Path]) -> None:
    incomplete = False
    for path in reversed(files):
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except OSError:
            incomplete = True
    for path in reversed(directories):
        try:
            path.rmdir()
        except FileNotFoundError:
            continue
        except OSError:
            incomplete = True
    message = (
        "Static site export failed; cleanup incomplete."
        if incomplete
        else ("Static site export failed.")
    )
    raise SiteExportError(message) from error


__all__ = ["StaticSiteExporter"]
