import argparse
import textwrap
from datetime import datetime
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import NamedTuple

from filelock import FileLock

_project_name = "modflowapi"
_project_root_path = Path(__file__).parent.parent
_version_py_path = _project_root_path / "modflowapi" / "version.py"
_citation_cff_path = _project_root_path / "CITATION.cff"


class Version(NamedTuple):
    """Semantic version number"""

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, version: str) -> "Version":
        t = version.split(".")

        vmajor = int(t[0])
        vminor = int(t[1])
        vpatch = int(t[2])

        return cls(major=vmajor, minor=vminor, patch=vpatch)

    @classmethod
    def from_file(cls, path: PathLike) -> "Version":
        lines = [
            line.rstrip("\n")
            for line in open(Path(path).expanduser().absolute(), "r")
        ]
        vmajor = vminor = vpatch = None
        for line in lines:
            line = line.strip()
            if not any(line):
                continue

            def get_ver(l):
                return l.split("=")[1]

            if "__version__" not in line:
                if "major" in line:
                    vmajor = int(get_ver(line))
                elif "minor" in line:
                    vminor = int(get_ver(line))
                elif "patch" in line or "micro" in line:
                    vpatch = int(get_ver(line))

        assert (
            vmajor is not None and vminor is not None and vpatch is not None
        ), "version string must follow semantic version format: major.minor.patch"
        return cls(major=vmajor, minor=vminor, patch=vpatch)


_initial_version = Version(0, 0, 1)
_current_version = Version.from_file(_version_py_path)


def update_version_py(timestamp: datetime, version: Version):
    with open(_version_py_path, "w") as f:
        f.write(
            f"# {_project_name} version file automatically created using "
            f"{Path(__file__).name} on {timestamp:%B %d, %Y %H:%M:%S}\n\n"
        )
        f.write(f"major = {version.major}\n")
        f.write(f"minor = {version.minor}\n")
        f.write(f"micro = {version.patch}\n")
        f.write("__version__ = f'{major}.{minor}.{micro}'\n")
    print(f"Updated {_version_py_path} to version {version}")

def update_citation_cff(timestamp: datetime, version: Version):
    lines = open(_citation_cff_path, "r").readlines()
    with open(_citation_cff_path, "w") as f:
        for line in lines:
            if line.startswith("version:"):
                line = f"version: {version}\n"
            f.write(line)
    print(f"Updated {_citation_cff_path} to version {version}")

def update_version(
    timestamp: datetime = datetime.now(),
    version: Version = None,
):
    lock_path = Path(_version_py_path.name + ".lock")
    try:
        lock = FileLock(lock_path)
        previous = Version.from_file(_version_py_path)
        version = (
            version
            if version
            else Version(previous.major, previous.minor, previous.patch)
        )

        with lock:
            update_version_py(timestamp, version)
            update_citation_cff(timestamp, version)
    finally:
        try:
            lock_path.unlink()
        except:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=f"Update {_project_name} version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Update version information stored in version.txt in the project root,
            as well as several other files in the repository. If --version is not
            provided, the version number will not be changed. A file lock is held
            to synchronize file access. The version tag must comply with standard
            '<major>.<minor>.<patch>' format conventions for semantic versioning.
            """
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        required=False,
        help="Specify the release version",
    )
    parser.add_argument(
        "-g",
        "--get",
        required=False,
        action="store_true",
        help="Just get the current version number, don't update anything (defaults to false)",
    )
    args = parser.parse_args()

    if args.get:
        print(_current_version)
    else:
        update_version(
            timestamp=datetime.now(),
            version=Version.from_string(args.version)
            if args.version
            else _current_version,
        )
