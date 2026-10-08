"""P4-001 output safety, deterministic ZIP and observable owned-only cleanup."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from types import SimpleNamespace
from typing import BinaryIO, Literal, NoReturn, cast
from zipfile import ZIP_STORED, ZipFile

import pytest

from src.site_export import (
    SiteExportError,
    SiteValidationError,
    StaticSiteBuild,
    StaticSiteExporter,
    StaticSiteFile,
)


def _build() -> StaticSiteBuild:
    return StaticSiteBuild(
        files=(
            StaticSiteFile(path="index.html", data=b"home"),
            StaticSiteFile(path="assets/p.png", data=b"image"),
            StaticSiteFile(path="assets/site.css", data=b"css"),
            StaticSiteFile(path="about.html", data=b"about"),
        )
    )


def _export(kind: Literal["folder", "zip"], build: StaticSiteBuild, destination: Path) -> Path:
    exporter = StaticSiteExporter()
    return (
        exporter.export_folder(build, destination)
        if kind == "folder"
        else exporter.export_zip(build, destination)
    )


@pytest.mark.parametrize("kind", ["folder", "zip"])
def test_exact_outputs_and_reproducibility(kind: Literal["folder", "zip"], tmp_path: Path) -> None:
    destination = tmp_path / "output"
    build = _build()
    assert _export(kind, build, destination) == destination
    expected = {item.path: item.data for item in build.files}
    if kind == "folder":
        actual = {
            path.relative_to(destination).as_posix(): path.read_bytes()
            for path in destination.rglob("*")
            if path.is_file()
        }
        assert actual == expected
        assert not (destination / "dist").exists()
    else:
        with ZipFile(destination) as archive:
            assert archive.namelist() == sorted(expected)
            assert archive.testzip() is None
            assert {name: archive.read(name) for name in archive.namelist()} == expected
            for info in archive.infolist():
                assert info.date_time == (1980, 1, 1, 0, 0, 0)
                assert info.compress_type == ZIP_STORED and info.create_system == 3
                assert info.external_attr >> 16 == stat.S_IFREG | 0o644
                assert not info.comment and not info.extra
        second = _export(
            kind, StaticSiteBuild(files=tuple(reversed(build.files))), tmp_path / "second"
        )
        assert second.read_bytes() == destination.read_bytes()


@pytest.mark.parametrize("kind", ["folder", "zip"])
@pytest.mark.parametrize(
    "issue",
    [
        "wrong_build",
        "list",
        "wrong_file",
        "empty_data",
        "mutable_data",
        "bad_path_type",
        "unsafe",
        "duplicate",
        "missing_home",
        "case",
        "device",
        "nested",
        "settings",
        "no_files",
    ],
)
def test_invalid_build_before_io(
    kind: Literal["folder", "zip"], issue: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file = StaticSiteFile(path="index.html", data=b"x")
    if issue == "wrong_build":
        build = cast("StaticSiteBuild", {})
    elif issue == "list":
        build = StaticSiteBuild(files=cast("tuple[StaticSiteFile, ...]", [file]))
    elif issue == "wrong_file":
        build = StaticSiteBuild(files=(cast("StaticSiteFile", {}),))
    elif issue in ("empty_data", "mutable_data"):
        data = b"" if issue == "empty_data" else cast("bytes", bytearray(b"x"))
        build = StaticSiteBuild(files=(StaticSiteFile(path="index.html", data=data),))
    elif issue == "duplicate":
        build = StaticSiteBuild(files=(file, file))
    elif issue == "no_files":
        build = StaticSiteBuild(files=())
    else:
        path: str = (
            cast("str", None)
            if issue == "bad_path_type"
            else {
                "unsafe": "../index.html",
                "missing_home": "about.html",
                "case": "INDEX.html",
                "device": "con.html",
                "nested": "assets/x.html",
                "settings": "settings.json",
            }[issue]
        )
        build = StaticSiteBuild(files=(StaticSiteFile(path=path, data=b"x"),))

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        raise AssertionError("Invalid artifact touched filesystem")

    monkeypatch.setattr(Path, "lstat", forbidden)
    with pytest.raises(SiteValidationError, match=r"^Invalid static site input\.$"):
        _export(kind, build, tmp_path / "output")


@pytest.mark.parametrize("kind", ["folder", "zip"])
@pytest.mark.parametrize(
    "issue",
    [
        "relative",
        "wrong_type",
        "missing_parent",
        "parent_file",
        "existing_file",
        "existing_empty",
        "existing_tree",
    ],
)
def test_destinations_unchanged(kind: Literal["folder", "zip"], issue: str, tmp_path: Path) -> None:
    destination = tmp_path / "output"
    sentinel = tmp_path / "sentinel"
    sentinel.write_bytes(b"user data")
    if issue == "relative":
        destination = Path("relative")
    elif issue == "wrong_type":
        destination = cast("Path", str(destination))
    elif issue == "missing_parent":
        destination = tmp_path / "missing" / "output"
    elif issue == "parent_file":
        destination = sentinel / "output"
    elif issue == "existing_file":
        destination.write_bytes(b"existing export")
    elif issue in ("existing_empty", "existing_tree"):
        destination.mkdir()
        if issue == "existing_tree":
            (destination / "keep").write_bytes(b"keep")
    before = {
        p.relative_to(tmp_path).as_posix(): p.read_bytes()
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    with pytest.raises(SiteValidationError):
        _export(kind, _build(), destination)
    after = {
        p.relative_to(tmp_path).as_posix(): p.read_bytes()
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    assert before == after
    if issue == "existing_empty":
        assert destination.is_dir()


@pytest.mark.parametrize("kind", ["folder", "zip"])
@pytest.mark.parametrize("mode", ["symlink", "reparse", "io_error"])
def test_link_reparse_and_inspection_failure(
    kind: Literal["folder", "zip"], mode: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = Path.lstat
    cause = PermissionError("private local path")

    def details(path: Path) -> os.stat_result:
        if path == tmp_path:
            if mode == "io_error":
                raise cause
            return cast(
                "os.stat_result",
                SimpleNamespace(
                    st_mode=stat.S_IFLNK if mode == "symlink" else stat.S_IFDIR,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
                    if mode == "reparse"
                    else 0,
                ),
            )
        return original(path)

    monkeypatch.setattr(Path, "lstat", details)
    error_type = SiteExportError if mode == "io_error" else SiteValidationError
    with pytest.raises(error_type) as error:
        _export(kind, _build(), tmp_path / "output")
    assert "private local path" not in str(error.value)
    if mode == "io_error":
        assert error.value.__cause__ is cause
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("kind", ["folder", "zip"])
def test_exclusive_creation_race_preserves_contender(
    kind: Literal["folder", "zip"], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "output"
    original_open = Path.open
    original_mkdir = Path.mkdir
    cause = FileExistsError("contender")
    if kind == "folder":

        def mkdir(path: Path, *args: object, **kwargs: object) -> NoReturn:
            original_mkdir(path)
            (path / "keep").write_bytes(b"contender")
            raise cause

        monkeypatch.setattr(Path, "mkdir", mkdir)
    else:

        def opening(path: Path, *args: object, **kwargs: object) -> NoReturn:
            with original_open(path, "wb") as stream:
                stream.write(b"contender")
            raise cause

        monkeypatch.setattr(Path, "open", opening)
    with pytest.raises(SiteExportError) as error:
        _export(kind, _build(), destination)
    assert error.value.__cause__ is cause
    if kind == "folder":
        assert (destination / "keep").read_bytes() == b"contender"
    else:
        monkeypatch.setattr(Path, "open", original_open)
        assert destination.read_bytes() == b"contender"


@pytest.mark.parametrize("kind", ["folder", "zip"])
@pytest.mark.parametrize(
    "cleanup",
    ["normal", "file_missing", "file_failure", "dir_missing", "dir_failure", "foreign_content"],
)
def test_write_failure_cleanup_is_owned_only(
    kind: Literal["folder", "zip"], cleanup: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "output"
    sentinel = tmp_path / "keep"
    sentinel.write_bytes(b"unrelated")
    original_open, original_unlink, original_rmdir = Path.open, Path.unlink, Path.rmdir
    cause = OSError("private content and local path")

    class BrokenStream:
        def __init__(self, stream: BinaryIO) -> None:
            self.stream = stream

        def __enter__(self) -> BrokenStream:
            return self

        def __exit__(self, *args: object) -> None:
            self.stream.close()

        def write(self, data: bytes) -> NoReturn:
            self.stream.write(data[:1])
            if cleanup == "foreign_content":
                with original_open(destination / "foreign", "wb") as stream:
                    stream.write(b"foreign")
            raise cause

    if kind == "folder":

        def opening(path: Path, *args: object, **kwargs: object) -> BinaryIO:
            return cast("BinaryIO", BrokenStream(cast("BinaryIO", original_open(path, "xb"))))

        monkeypatch.setattr(Path, "open", opening)
    else:

        def fail(*args: object, **kwargs: object) -> NoReturn:
            raise cause

        monkeypatch.setattr(ZipFile, "writestr", fail)
    if cleanup in ("file_missing", "file_failure"):

        def unlink(path: Path, *args: object, **kwargs: object) -> None:
            if cleanup == "file_failure":
                raise PermissionError("private cleanup detail")
            original_unlink(path)
            raise FileNotFoundError

        monkeypatch.setattr(Path, "unlink", unlink)
    if cleanup in ("dir_missing", "dir_failure"):

        def rmdir(path: Path) -> None:
            if cleanup == "dir_failure":
                raise PermissionError("private cleanup detail")
            original_rmdir(path)
            raise FileNotFoundError

        monkeypatch.setattr(Path, "rmdir", rmdir)
    with pytest.raises(SiteExportError) as error:
        _export(kind, _build(), destination)
    monkeypatch.setattr(Path, "open", original_open)
    assert error.value.__cause__ is cause
    assert "private" not in str(error.value) and str(destination) not in str(error.value)
    expected_incomplete = cleanup == "file_failure" or (
        kind == "folder" and cleanup in ("dir_failure", "foreign_content")
    )
    assert ("cleanup incomplete" in str(error.value)) == expected_incomplete
    assert sentinel.read_bytes() == b"unrelated"
    if kind == "folder" and cleanup == "foreign_content":
        assert (destination / "foreign").read_bytes() == b"foreign"
    elif not expected_incomplete:
        assert not destination.exists()


def test_failure_after_assets_directory_and_file_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = Path.open
    cause = PermissionError("asset write blocked")

    def opening(path: Path, *args: object, **kwargs: object) -> BinaryIO:
        if path.name == "p.png":
            raise cause
        return cast("BinaryIO", original(path, "xb"))

    monkeypatch.setattr(Path, "open", opening)
    destination = tmp_path / "output"
    with pytest.raises(SiteExportError) as error:
        StaticSiteExporter().export_folder(_build(), destination)
    assert error.value.__cause__ is cause
    assert not destination.exists()


@pytest.mark.parametrize("kind", ["folder", "zip"])
def test_build_capacity_limit_before_io(
    kind: Literal["folder", "zip"], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = b"x" * (15 * 1024 * 1024)
    files = (
        StaticSiteFile(path="index.html", data=data),
        *(StaticSiteFile(path=f"p{number}.html", data=data) for number in range(9)),
    )
    # At the exact 150 MiB boundary, validation completes before destination validation.
    with pytest.raises(SiteValidationError, match="Invalid export destination"):
        _export(kind, StaticSiteBuild(files=files), Path("relative"))

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        raise AssertionError("Oversized build touched filesystem")

    monkeypatch.setattr(Path, "lstat", forbidden)
    with pytest.raises(SiteValidationError, match="Invalid static site input"):
        _export(
            kind,
            StaticSiteBuild(files=(*files, StaticSiteFile(path="extra.html", data=b"x"))),
            tmp_path / "output",
        )
