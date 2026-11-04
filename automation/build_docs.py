"""Build the project documentation: API reference (Doxygen) + site (MkDocs).

Doxygen writes the API reference into docs/api (generated, ignored by git);
MkDocs then builds the whole docs/ directory into build/docs/site.
Both tools treat problems as errors: an undocumented public entity fails
Doxygen (WARN_AS_ERROR), a broken link fails MkDocs (--strict).

Usage:
    python automation/build_docs.py
    python automation/build_docs.py --serve   # local preview at http://127.0.0.1:8000
"""

import sys

from common import PROJECT_ROOT, run

SITE_DIR = PROJECT_ROOT / "build" / "docs" / "site"

run(["doxygen", "Doxyfile"])

if "--serve" in sys.argv[1:]:
    run([sys.executable, "-m", "mkdocs", "serve"])
    sys.exit(0)

run([sys.executable, "-m", "mkdocs", "build", "--strict"])
print(f"documentation: {SITE_DIR / 'index.html'}")
