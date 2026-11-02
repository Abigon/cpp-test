"""Build the Debug configuration and run all tests through CTest.

Writes a JUnit report to build/test-report.xml for CI.
"""

from common import BUILD_DIR, build, run

build("Debug")
run(["ctest", "--test-dir", BUILD_DIR.name, "-C", "Debug", "--output-on-failure",
     "--output-junit", "test-report.xml"])