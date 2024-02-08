from pathlib import Path
from platform import system


def amend_libmf6_path(path) -> str:
    ext = Path(path).suffix
    path = str(path)
    os = system().lower()
    if os == "windows":
        if not ext:
            path += ".dll"
        path = str(Path(path).absolute())
    elif os == "linux":
        if not ext:
            path += ".so"
        if not path.startswith("./"):
            if not path.startswith("/"):
                path = "./" + path
    elif os == "darwin" and not ext:
        path += ".dylib"
    return path
