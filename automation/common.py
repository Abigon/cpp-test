"""Common helpers for the project automation scripts.

All scripts run from any directory: paths are computed from this file,
not from the current working directory.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
TOOLCHAIN = BUILD_DIR / "conan_toolchain.cmake"

CONFIGURATIONS = ("Debug", "Release")


def run(command: list[str]) -> None:
    """Run a command from the project root; stop the script if it fails."""
    print("+", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"command failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)


def profile(configuration: str) -> str:
    """Conan profile for Debug or Release, relative to the project root."""
    return f"profiles/windows-msvc-{configuration.lower()}"


def conan_install(configuration: str) -> None:
    run([
        "conan", "install", ".",
        f"--output-folder={BUILD_DIR.name}",
        "-pr:h", profile(configuration),
        "-pr:b", profile(configuration),
        "--build=missing",
    ])


def configure() -> None:
    """Configure CMake with the Conan toolchain."""
    run(["cmake", "-S", ".", "-B", BUILD_DIR.name, f"-DCMAKE_TOOLCHAIN_FILE={TOOLCHAIN}"])


def ensure_generated() -> None:
    """Generate project files if the build directory does not exist yet."""
    if not (BUILD_DIR / "CMakeCache.txt").exists():
        print("build directory not found, generating project files first")
        for configuration in CONFIGURATIONS:
            conan_install(configuration)
        configure()


def build(configuration: str) -> None:
    ensure_generated()
    run(["cmake", "--build", BUILD_DIR.name, "--config", configuration])