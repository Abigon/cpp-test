"""Measure test coverage with OpenCppCoverage.

Builds Debug, runs AppTestRunner under OpenCppCoverage and writes:
    build/coverage/html/index.html   -- report for humans
    build/coverage/coverage.xml      -- Cobertura XML for CI
Prints a per-file table; on GitHub Actions appends it to the job summary.

Usage:
    python automation/run_coverage.py             # measure and report
    python automation/run_coverage.py --min 70    # also fail if total line coverage < 70%
"""

import os
import shutil
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from common import BUILD_DIR, PROJECT_ROOT, build, run

KNOWN_PATHS = [Path(r"C:\Program Files\OpenCppCoverage\OpenCppCoverage.exe")]
COVERAGE_DIR = BUILD_DIR / "coverage"
REPORT_XML = COVERAGE_DIR / "coverage.xml"
TEST_RUNNER = BUILD_DIR / "bin" / "Debug" / "AppTestRunner.exe"


def find_tool() -> str:
    found = shutil.which("OpenCppCoverage")
    if found:
        return found
    for path in KNOWN_PATHS:
        if path.is_file():
            return str(path)
    print("OpenCppCoverage not found: winget install OpenCppCoverage.OpenCppCoverage", file=sys.stderr)
    sys.exit(1)


def minimum_from_args() -> float | None:
    args = sys.argv[1:]
    if "--min" in args:
        return float(args[args.index("--min") + 1])
    return None


def coverage_table() -> tuple[float, list[tuple[str, float, int, int]]]:
    root = ElementTree.parse(REPORT_XML).getroot()
    total = float(root.get("line-rate", 0)) * 100
    rows = []
    for cls in root.iter("class"):
        lines = cls.findall("./lines/line")
        covered = sum(1 for line in lines if int(line.get("hits", 0)) > 0)
        name = Path(cls.get("filename", "")).name
        rows.append((name, float(cls.get("line-rate", 0)) * 100, covered, len(lines)))
    return total, rows


def main() -> None:
    build("Debug")
    tool = find_tool()
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    run([
        tool, "--quiet",
        "--sources", str(PROJECT_ROOT / "src" / "App"),
        "--excluded_sources", "*\\Tests\\*",
        "--export_type", f"html:{COVERAGE_DIR / 'html'}",
        "--export_type", f"cobertura:{REPORT_XML}",
        "--", str(TEST_RUNNER),
    ])

    total, rows = coverage_table()
    lines = ["| File | Lines | Covered |", "|---|---|---|"]
    lines += [f"| {name} | {covered}/{count} | {rate:.0f}% |" for name, rate, covered, count in rows]
    lines.append(f"| **Total** | | **{total:.0f}%** |")
    table = "\n".join(lines)
    print(table)
    print(f"HTML report: {COVERAGE_DIR / 'html' / 'index.html'}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("## Test coverage\n\n" + table + "\n")

    minimum = minimum_from_args()
    if minimum is not None and total < minimum:
        print(f"coverage {total:.0f}% is below the required {minimum:.0f}%", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
    