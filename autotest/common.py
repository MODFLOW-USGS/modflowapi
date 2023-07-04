"""Common functions for tests. For pytest fixtures, see conftest.py."""

from pathlib import Path
from tempfile import gettempdir

import pytest
from filelock import FileLock

from modflowapi.util import get_libmf6

try:
    libmf6 = get_libmf6()
except FileNotFoundError:
    libmf6 = "libmf6"


_mf6_examples = "mf6_examples"
_mf6_examples_path = Path(gettempdir()) / _mf6_examples
_mf6_examples_lock = FileLock(Path(gettempdir()) / f"{_mf6_examples}.lock")


def get_mf6_examples_path() -> Path:
    pytest.importorskip("modflow_devtools")
    from modflow_devtools.download import download_and_unzip

    # use file lock so mf6 distribution is downloaded once,
    # even when tests are run in parallel with pytest-xdist
    _mf6_examples_lock.acquire()
    try:
        if not _mf6_examples_path.is_dir():
            _mf6_examples_path.mkdir(exist_ok=True)
            download_and_unzip(
                url="https://github.com/MODFLOW-USGS/modflow6-examples/releases/download/current/modflow6-examples.zip",
                path=_mf6_examples_path,
                verbose=True,
            )
        return _mf6_examples_path
    finally:
        _mf6_examples_lock.release()


def is_nested(namfile) -> bool:
    p = Path(namfile)
    if not p.is_file() or not p.name.endswith(".nam"):
        raise ValueError(f"Expected a namfile path, got {p}")

    return p.parent.parent.name != _mf6_examples
