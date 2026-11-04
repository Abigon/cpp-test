"""Build the project with AddressSanitizer and run the tests under it.

The instrumented build lives in its own directory (build-asan) so the regular
build stays fast and unchanged. It reuses the Conan toolchain from build/.

Usage:
    python automation/run_asan.py
"""

from common import build_dir, cmake_build, configure, ensure_generated, relative, run

ASAN_BUILD_DIR = build_dir("Debug", root="build-asan")

ensure_generated("Debug")
configure("Debug", ASAN_BUILD_DIR, ["-DENABLE_ASAN=ON"])
cmake_build(ASAN_BUILD_DIR, "Debug")
run(["ctest", "--test-dir", relative(ASAN_BUILD_DIR), "-C", "Debug", "--output-on-failure"])
    