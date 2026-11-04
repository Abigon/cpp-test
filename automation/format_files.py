"""Format all sources with clang-format, or check them with --check."""

import sys

from common import build_dir, ensure_generated, relative, run

ensure_generated()
target = "format-check" if "--check" in sys.argv[1:] else "format"
run(["cmake", "--build", relative(build_dir("Debug")), "--target", target])
