"""Run clang-tidy over the project.

Windows: Visual Studio ships clang-tidy and runs it as part of the build:
MSBuild passes each file's real compile flags, so no compile_commands.json
is needed.
Linux: clang-tidy reads each file's flags from build/Debug/compile_commands.json,
which configure() exports for Makefiles.
Findings are errors (see .clang-tidy: WarningsAsErrors), so the run fails.

Usage:
    python automation/run_tidy.py
"""

from common import IS_WINDOWS, PROJECT_ROOT, build_dir, cmake_build, ensure_generated, relative, run

ensure_generated()
if IS_WINDOWS:
    run([
        "cmake", "--build", relative(build_dir("Debug")), "--config", "Debug",
        "--",
        "/p:RunCodeAnalysis=true",
        "/p:EnableClangTidyCodeAnalysis=true",
        "/p:EnableMicrosoftCodeAnalysis=false",
    ])
else:
    cmake_build(build_dir("Debug"), "Debug")  # generated headers and the database must exist
    sources = sorted((PROJECT_ROOT / "src").rglob("*.cpp"))
    run(["clang-tidy", "-p", relative(build_dir("Debug")), *(relative(s) for s in sources)])