"""Format all sources with clang-format, or check them with --check."""

import sys

from common import BUILD_DIR, ensure_generated, run

ensure_generated()
target = "format-check" if "--check" in sys.argv[1:] else "format"
run(["cmake", "--build", BUILD_DIR.name, "--target", target])
