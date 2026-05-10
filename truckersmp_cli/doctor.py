"""
Diagnostics command for truckersmp-cli.

Licensed under MIT.
"""

import os

from .utils import check_libsdl2
from .variables import Args, Dir, File


def _status(ok, label, detail=""):
    """Print one diagnostic status line."""
    mark = "OK" if ok else "FAIL"
    if detail:
        print(f"[{mark}] {label}: {detail}")
    else:
        print(f"[{mark}] {label}")
    return ok


def _check_path(label, path, mode=os.R_OK):
    """Check whether a path exists and is accessible."""
    return _status(os.access(path, mode), label, path)


def run_doctor(version_string):
    """Run basic diagnostics for the local truckersmp-cli setup."""
    print("truckersmp-cli doctor")
    print()
    print(f"Version: {version_string}")
    print(f"Config file: {Args.configfile}")
    print(f"Data directory: {Dir.truckersmp_cli_data}")
    print()

    checks = []

    checks.append(_status(
        True,
        "Selected runner",
        "Proton" if Args.proton else "Wine",
    ))
    checks.append(_check_path(
        "Data directory exists",
        Dir.truckersmp_cli_data,
        os.R_OK | os.W_OK | os.X_OK,
    ))
    checks.append(_check_path(
        "Inject program exists",
        File.inject_exe,
        os.R_OK,
    ))
    checks.append(_status(
        check_libsdl2(),
        "SDL2 library found",
        File.sdl2_soname,
    ))

    print()
    print("Steam files:")

    steam_paths = [
        os.path.join(Dir.XDG_DATA_HOME, "Steam", File.steamlibvdf_inner),
        os.path.join(os.path.expanduser("~/.steam"), File.steamlibvdf_inner),
        os.path.join(
            os.path.expanduser("~/.steam/debian-installation"),
            File.steamlibvdf_inner,
        ),
        os.path.join(Dir.flatpak_steamdir, File.steamlibvdf_inner),
    ]

    found_steam_library = False
    for path in steam_paths:
        if os.path.isfile(path):
            found_steam_library = True
            _status(True, "libraryfolders.vdf found", path)

    if not found_steam_library:
        checks.append(_status(
            False,
            "libraryfolders.vdf found",
            "No known path found",
        ))
    else:
        checks.append(True)

    print()
    if all(checks):
        print("Doctor result: OK")
        return 0

    print("Doctor result: issues found")
    return 1
