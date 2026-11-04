"""Build the Debug configuration and run all tests through CTest.

Writes a JUnit report to build/test-report.xml for CI.
"""

from common import build, build_dir, relative, run

build("Debug")
run(["ctest", "--test-dir", relative(build_dir("Debug")), "-C", "Debug", "--output-on-failure",
     "--output-junit", "test-report.xml"])