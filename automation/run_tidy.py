"""Run clang-tidy over the project through MSBuild code analysis.

Visual Studio ships clang-tidy and can run it as part of the build: MSBuild
passes each file's real compile flags, so no compile_commands.json is needed.
Findings are errors (see .clang-tidy: WarningsAsErrors), so the build fails.

Usage:
    python automation/run_tidy.py
"""

from common import BUILD_DIR, ensure_generated, run

ensure_generated()
run([
    "cmake", "--build", BUILD_DIR.name, "--config", "Debug",
    "--",
    "/p:RunCodeAnalysis=true",
    "/p:EnableClangTidyCodeAnalysis=true",
    "/p:EnableMicrosoftCodeAnalysis=false",
])