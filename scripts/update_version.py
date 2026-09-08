import argparse
import sys
import textwrap
from datetime import datetime
from os.path import basename
from pathlib import Path

from filelock import FileLock
from packaging.version import Version

_project_name = "modflowapi"
_project_root_path = Path(__file__).parent.parent
_version_txt_path = _project_root_path / "version.txt"
_version_py_path = _project_root_path / "modflowapi" / "version.py"
_citation_cff_path = _project_root_path / "CITATION.cff"

_current_version = Version(_version_txt_path.read_text().strip())


def log_update(path, version: Version):
    print(f"Updated {path} with version {version}", file=sys.stderr)


def release_version() -> Version:
    """The current development version with any development segment (e.g. '.dev0') removed."""
    return Version(_current_version.base_version)


def post_release_version() -> Version:
    """Development version for the next cycle: minor incremented, '.dev0' suffix."""
    version = Version(_current_version.base_version)
    return Version(f"{version.major}.{version.minor + 1}.0.dev0")


def update_version_txt(version: Version):
    with open(_version_txt_path, "w") as f:
        f.write(str(version))
    log_update(_version_txt_path, version)


def update_version_py(timestamp: datetime, version: Version):
    with open(_version_py_path, "w") as f:
        f.write(f"# {_project_name} version file automatically created using...{basename(__file__)}\n")
        f.write(f"# created on...{timestamp.strftime('%B %d, %Y %H:%M:%S')}\n")
        f.write(f'__version__ = "{version}"\n')
    log_update(_version_py_path, version)


def update_citation_cff(timestamp: datetime, version: Version):
    lines = open(_citation_cff_path, "r").readlines()
    with open(_citation_cff_path, "w") as f:
        for line in lines:
            if line.startswith("version:"):
                line = f"version: {version}\n"
            elif line.startswith("date-released:"):
                line = f"date-released: '{timestamp.strftime('%Y-%m-%d')}'\n"
            f.write(line)
    log_update(_citation_cff_path, version)


def update_version(timestamp: datetime = datetime.now(), version: Version = None):
    lock_path = Path(_version_py_path.name + ".lock")
    try:
        lock = FileLock(lock_path)
        version = version if version else _current_version

        with lock:
            update_version_txt(version)
            update_version_py(timestamp, version)
            update_citation_cff(timestamp, version)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=f"Update {_project_name} version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Update version information in version.txt in the project root, as
            well as several other files in the repository, and print the new
            version. If none of --version, --release or --post-release is
            provided, the version number is not changed. A file lock is held to
            synchronize file access. The version tag must be standard
            '<major>.<minor>.<patch>' format for semantic versioning.
            """
        ),
    )
    parser.add_argument("-v", "--version", required=False, help="Specify the release version")
    parser.add_argument(
        "-r",
        "--release",
        required=False,
        action="store_true",
        help="Use the current development version with its development segment (e.g. '.dev0') removed",
    )
    parser.add_argument(
        "-p",
        "--post-release",
        required=False,
        action="store_true",
        help="Use the development version for the next cycle: the minor version incremented, with a '.dev0' suffix",
    )
    parser.add_argument(
        "--dry-run",
        required=False,
        action="store_true",
        help="Print the version that would be written, and exit without writing",
    )
    args = parser.parse_args()

    if args.post_release:
        version = post_release_version()
    elif args.release:
        version = release_version()
    elif args.version:
        version = Version(args.version)
    else:
        version = _current_version

    if not args.dry_run:
        update_version(timestamp=datetime.now(), version=version)
    print(version)
