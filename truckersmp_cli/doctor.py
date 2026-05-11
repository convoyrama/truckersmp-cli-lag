"""
Diagnostics command for truckersmp-cli.

Licensed under MIT.
"""

import json
import os

from .utils import check_libsdl2
from .variables import Args, Dir, File


def _make_check(check_id, ok, label, detail=""):
    """Create one diagnostic check result."""
    return {
        "id": check_id,
        "ok": ok,
        "status": "ok" if ok else "fail",
        "label": label,
        "detail": detail,
    }


def _check_path(check_id, label, path, mode=os.R_OK):
    """Check whether a path exists and is accessible."""
    return _make_check(check_id, os.access(path, mode), label, path)


def _find_steam_library_checks():
    """Find Steam libraryfolders.vdf files in known locations."""
    steam_paths = [
        os.path.join(Dir.XDG_DATA_HOME, "Steam", File.steamlibvdf_inner),
        os.path.join(os.path.expanduser("~/.steam"), File.steamlibvdf_inner),
        os.path.join(
            os.path.expanduser("~/.steam/debian-installation"),
            File.steamlibvdf_inner,
        ),
        os.path.join(Dir.flatpak_steamdir, File.steamlibvdf_inner),
    ]

    checks = []
    for path in steam_paths:
        if os.path.isfile(path):
            checks.append(_make_check(
                "steam_libraryfolders",
                True,
                "libraryfolders.vdf found",
                path,
            ))

    if not checks:
        checks.append(_make_check(
            "steam_libraryfolders",
            False,
            "libraryfolders.vdf found",
            "No known path found",
        ))

    return checks


def _build_report(version_string):
    """Build diagnostics report data."""
    checks = [
        _make_check(
            "selected_runner",
            True,
            "Selected runner",
            "Proton" if Args.proton else "Wine",
        ),
        _check_path(
            "data_directory",
            "Data directory exists",
            Dir.truckersmp_cli_data,
            os.R_OK | os.W_OK | os.X_OK,
        ),
        _check_path(
            "inject_program",
            "Inject program exists",
            File.inject_exe,
            os.R_OK,
        ),
        _make_check(
            "sdl2",
            check_libsdl2(),
            "SDL2 library found",
            File.sdl2_soname,
        ),
    ]
    checks.extend(_find_steam_library_checks())

    ok = all(check["ok"] for check in checks)

    return {
        "ok": ok,
        "status": "ok" if ok else "issues_found",
        "version": version_string,
        "config_file": Args.configfile,
        "data_directory": Dir.truckersmp_cli_data,
        "runner": "proton" if Args.proton else "wine",
        "checks": checks,
    }


def _print_text_report(report):
    """Print diagnostics report in human-readable text format."""
    print("truckersmp-cli doctor")
    print()
    print(f"Version: {report['version']}")
    print(f"Config file: {report['config_file']}")
    print(f"Data directory: {report['data_directory']}")
    print()

    for check in report["checks"]:
        if check["id"] == "steam_libraryfolders":
            continue
        print(f"[{check['status'].upper()}] {check['label']}: {check['detail']}")

    print()
    print("Steam files:")

    for check in report["checks"]:
        if check["id"] == "steam_libraryfolders":
            print(f"[{check['status'].upper()}] {check['label']}: {check['detail']}")

    print()
    if report["ok"]:
        print("Doctor result: OK")
    else:
        print("Doctor result: issues found")


def run_doctor(version_string):
    """Run basic diagnostics for the local truckersmp-cli setup."""
    report = _build_report(version_string)

    if Args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text_report(report)

    return 0 if report["ok"] else 1
