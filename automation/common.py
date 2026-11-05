"""Common helpers for the project automation scripts.

All scripts run from any directory: paths are computed from this file,
not from the current working directory.

Windows and Linux differ in one thing: the Visual Studio generator keeps
Debug and Release in one build tree (build/, binaries in build/bin/<Config>),
while Makefiles keep one configuration per tree (build/<Config>, binaries in
build/<Config>/bin). Everything else goes through the same commands.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = "App"  # the only place in automation/ that names the project
PROFILES_DIR = PROJECT_ROOT / "profiles"
IS_WINDOWS = sys.platform == "win32"

CONFIGURATIONS = ("Debug", "Release")


def run(command: list[str]) -> None:
    """Run a command from the project root; stop the script if it fails."""
    print("+", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"command failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)


def profile(configuration: str) -> str:
    """Path to the Conan profile for this platform and configuration."""
    platform = "windows-msvc" if IS_WINDOWS else "linux-gcc"
    return f"profiles/{platform}-{configuration.lower()}"


def build_dir(configuration: str, root: str = "build") -> Path:
    """Build tree for a configuration: one shared tree on Windows, one per configuration on Linux.

    `root` is the tree's top directory; the sanitizer build uses "build-asan".
    Keeping the platforms apart matters even for one machine: a project on C:
    is visible from WSL as /mnt/c, and CMakeCache.txt remembers absolute paths.
    """
    return PROJECT_ROOT / root if IS_WINDOWS else PROJECT_ROOT / root / configuration


def bin_dir(configuration: str) -> Path:
    """Where the executables of a configuration end up."""
    return build_dir(configuration) / "bin" / configuration if IS_WINDOWS else build_dir(configuration) / "bin"


def toolchain(configuration: str) -> Path:
    return build_dir(configuration) / "conan_toolchain.cmake"


def relative(path: Path) -> str:
    """Path as CMake and Conan see it: relative to the project root, forward slashes."""
    return path.relative_to(PROJECT_ROOT).as_posix()


def conan_install(configuration: str) -> None:
    run([
        "conan", "install", ".",
        f"--output-folder={relative(build_dir(configuration))}",
        "-pr:h", profile(configuration),
        "-pr:b", profile(configuration),
        "--build=missing",
    ])


def configure(configuration: str, build_tree: Path | None = None, extra: list[str] = ()) -> None:
    """Configure a CMake build tree with the Conan toolchain.

    On Linux the generator is single-configuration, so the configuration is
    fixed here with CMAKE_BUILD_TYPE and a compile_commands.json is exported
    for clang-tidy. On Windows --config is chosen at build time instead.
    """
    tree = build_tree or build_dir(configuration)
    command = ["cmake", "-S", ".", "-B", relative(tree), f"-DCMAKE_TOOLCHAIN_FILE={toolchain(configuration)}"]
    if not IS_WINDOWS:
        command += [f"-DCMAKE_BUILD_TYPE={configuration}", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]
    run(command + list(extra))


def ensure_generated(configuration: str = "Debug") -> None:
    """Generate project files for a configuration if its build tree does not exist yet."""
    if (build_dir(configuration) / "CMakeCache.txt").exists():
        return
    print("build directory not found, generating project files first")
    if IS_WINDOWS:
        for each in CONFIGURATIONS:  # one tree holds both configurations
            conan_install(each)
    else:
        conan_install(configuration)
    configure(configuration)


def cmake_build(build_tree: Path, configuration: str) -> None:
    """Build a tree; --config only means something to multi-configuration generators."""
    command = ["cmake", "--build", relative(build_tree)]
    if IS_WINDOWS:
        command += ["--config", configuration]
    run(command)


def build(configuration: str) -> None:
    ensure_generated(configuration)
    cmake_build(build_dir(configuration), configuration)
