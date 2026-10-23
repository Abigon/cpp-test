"""Remove build artifacts: everything listed in .gitignore (build/, __pycache__/, ...).

Usage:
    python automation/clean.py            # delete
    python automation/clean.py --dry-run  # only show what would be deleted
"""

import subprocess
import sys

from common import PROJECT_ROOT

dry_run = "--dry-run" in sys.argv[1:]

# -X: only files ignored by git; -d: directories too; -n: show, -f: delete
preview = subprocess.run(["git", "clean", "-Xdn"], cwd=PROJECT_ROOT, capture_output=True, text=True)
if preview.returncode != 0:
    print(preview.stderr.strip(), file=sys.stderr)
    sys.exit(preview.returncode)

if not preview.stdout.strip():
    print("nothing to clean")
    sys.exit(0)

print(preview.stdout.strip(), flush=True)
if dry_run:
    sys.exit(0)

result = subprocess.run(["git", "clean", "-Xdf"], cwd=PROJECT_ROOT)
sys.exit(result.returncode)
