import os
import platform
import shutil
from pathlib import Path
from typing import Optional


def get_libmf6_name(sysinfo: Optional[str] = None) -> str:
    """Get name to libmf6 based on ``platform.system()`` information."""
    if sysinfo is None:
        sysinfo = platform.system()
    if sysinfo == "Windows":
        return "libmf6.dll"
    elif sysinfo == "Linux":
        return "libmf6.so"
    elif sysinfo == "Darwin":
        return "libmf6.dylib"
    else:
        raise NotImplementedError(f"system not supported: {sysinfo!r}")


def get_libmf6() -> Path:
    """Get path to libmf6 based on environment variable or PATH with mf6.

    To specify directly, set the environment variable `LIBMF6` to the path of
    the library to test.

    Otherwise, check for the environment variable `MODFLOW_BIN_PATH` as used by
    modflowpy/install-modflow-action to find the mf6 executable.

    Lastly, find the mf6 executable from the PATH environment, and
    try to find the library in the same directory as the executable.
    """
    if "LIBMF6" in os.environ:
        lib_path = Path(os.environ["LIBMF6"])
    else:
        if "MODFLOW_BIN_PATH" in os.environ:
            mf6 = shutil.which("mf6", path=os.environ["MODFLOW_BIN_PATH"])
        else:
            mf6 = shutil.which("mf6")
        if mf6 is None:
            raise FileNotFoundError("cannot find mf6 on PATH")
        mf6 = Path(mf6)
        lib_name = get_libmf6_name()
        lib_path = mf6.parent.parent / "lib" / lib_name
        if not lib_path.exists():
            lib_path = mf6.parent / lib_name
    if lib_path.exists():
        return lib_path
    raise FileNotFoundError(f"{lib_path} not found")
