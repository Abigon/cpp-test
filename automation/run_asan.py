"""Build the project with AddressSanitizer and run the tests under it.

The instrumented build lives in its own directory (build-asan) so the regular
build stays fast and unchanged. It reuses the Conan toolchain from build/.

Usage:
    python automation/run_asan.py
"""

from common import PROJECT_ROOT, TOOLCHAIN, ensure_generated, run

ASAN_BUILD_DIR = PROJECT_ROOT / "build-asan"

ensure_generated()
run(["cmake", "-S", ".", "-B", ASAN_BUILD_DIR.name,
     f"-DCMAKE_TOOLCHAIN_FILE={TOOLCHAIN}", "-DENABLE_ASAN=ON"])
run(["cmake", "--build", ASAN_BUILD_DIR.name, "--config", "Debug"])
run(["ctest", "--test-dir", ASAN_BUILD_DIR.name, "-C", "Debug", "--output-on-failure"])