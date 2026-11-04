# App

[![build](https://github.com/Abigon/cpp-test/actions/workflows/build.yml/badge.svg)](https://github.com/Abigon/cpp-test/actions/workflows/build.yml)
[![tests](https://github.com/Abigon/cpp-test/actions/workflows/tests.yml/badge.svg)](https://github.com/Abigon/cpp-test/actions/workflows/tests.yml)
[![code-quality](https://github.com/Abigon/cpp-test/actions/workflows/code-quality.yml/badge.svg)](https://github.com/Abigon/cpp-test/actions/workflows/code-quality.yml)
[![docs](https://github.com/Abigon/cpp-test/actions/workflows/docs.yml/badge.svg)](https://github.com/Abigon/cpp-test/actions/workflows/docs.yml)

Учебный проект курса «Инженерный C++»: консольное приложение `App`, которое читает
настройки из `config.json` и выводит их. Логика вынесена в статическую библиотеку
`AppLib` и покрыта юнит-тестами; сборка, тесты и проверки качества автоматизированы
скриптами Python и выполняются в GitHub Actions.

## Системные требования

### Windows

- Windows 10/11 (x64);
- Visual Studio 2022 или новее с компонентами «Разработка классических приложений на C++»
  и «C++ AddressSanitizer»;
- CMake 3.25+;
- Python 3;
- Conan 2 (`pip install conan`);
- OpenCppCoverage — для измерения покрытия;
- для сборки документации — Doxygen и пакеты из `requirements-docs.txt`.

### Linux (Ubuntu 24.04 или WSL)

- GCC 14, CMake, clang-tidy, clang-format:
  `sudo apt install -y g++-14 cmake make clang-tidy clang-format pipx`;
- Conan 2: `pipx install conan`;
- Python 3 — скрипты запускаются командой `python3`, а не `python`.

Скрипты в `automation/` одни и те же для обеих платформ. Различаются каталоги сборки:
на Windows бинарники лежат в `build/bin/<Config>/`, на Linux — в `build/<Config>/bin/`
(`App`, `AppTestRunner`, без `.exe`). Покрытие измеряется только на Windows.

## Сборка и запуск

Все команды выполняются из корня проекта. Windows (PowerShell):

```powershell
# 1. Install Conan dependencies and configure CMake (Debug and Release)
python automation/generate_project_files.py

# 2. Build the Debug configuration
python automation/build_debug.py

# 3. Run the app (config.json is read from the current directory)
.\build\bin\Debug\App.exe
```

Linux (bash, в том числе WSL):

```bash
python3 automation/generate_project_files.py
python3 automation/build_debug.py
./build/Debug/bin/App
```

- Release-сборка: `python automation/build_release.py`, бинарник — `build\bin\Release\App.exe`
  (на Linux — `build/Release/bin/App`).
- Полная очистка артефактов сборки: `python automation/clean.py`
  (`--dry-run` — только показать, что будет удалено).
- Общие пути, конфигурации и профили Conan для всех скриптов заданы в `automation/common.py`;
  там же собраны все различия между Windows и Linux.

## Тестирование

Тесты на GoogleTest лежат в `src/App/Tests/` и собираются в `AppTestRunner`.

```powershell
# Build Debug and run all tests through CTest (report: build/test-report.xml)
python automation/run_tests.py

# Coverage with OpenCppCoverage (report: build/coverage/html/index.html)
python automation/run_coverage.py --min 70

# Separate build in build-asan/ and tests under AddressSanitizer
python automation/run_asan.py
```

- `run_tests.py` — сборка Debug и запуск тестов; отчёт JUnit для CI.
- `run_coverage.py` — покрытие строк; с `--min 70` падает, если покрытие ниже порога.
- `run_asan.py` — отдельная инструментированная сборка в `build-asan/`, ловит ошибки
  памяти (выход за границы буфера, use-after-free) в момент обращения.

## Контроль качества кода

```powershell
# Check formatting (without --check: format all files)
python automation/format_files.py --check

# Static analysis with clang-tidy
python automation/run_tidy.py
```

- правила форматирования — `.clang-format` (на основе стиля Microsoft);
- правила анализатора — `.clang-tidy`, любая находка — ошибка;
- предупреждения компилятора — ошибки (`/W4 /WX`), см. `cmake/CompilerWarnings.cmake`.

## Документация

Опубликованная документация: https://abigon.github.io/cpp-test/

- **Справочник API** генерируется Doxygen из комментариев `///` в заголовочных
  файлах `src/App` (конфигурация — `Doxyfile`).
- **Страницы о проекте** (обзор, архитектура, руководство разработчика) —
  Markdown-файлы в `docs/`, сайт из них собирает MkDocs (конфигурация — `mkdocs.yml`).

Сайт публикуется на GitHub Pages автоматически при каждом push в `master`.

```powershell
# Build the API reference and the site into build/docs/site
python automation/build_docs.py

# Local preview with live reload at http://127.0.0.1:8000
python automation/build_docs.py --serve
```

## Структура проекта

```text
project/
├── .github/workflows/   # CI: build.yml, tests.yml, code-quality.yml, docs.yml
├── automation/          # Python scripts: generate, build, test, check, clean
├── cmake/               # CMake modules: warnings, sanitizers, clang-format
├── profiles/            # Conan profiles: Windows MSVC and Linux GCC 14
├── src/App/             # subproject: AppLib, App and their sources
│   └── Tests/           # GoogleTest tests -> AppTestRunner
├── CMakeLists.txt       # root project: C++23, dependencies, output dir
├── conanfile.txt        # dependencies: nlohmann_json, gtest
├── config.json          # app configuration read at startup
└── protection.json      # branch protection rules for master
```

Бинарники собираются в `build/bin/<Config>/` на Windows и в `build/<Config>/bin/` на Linux.

## Непрерывная интеграция (CI)

CI состоит из четырёх независимых workflow. Все они запускаются на `windows-latest`
и `ubuntu-latest` при `push` в `master` и при каждом Pull Request, выполняются
параллельно и падают независимо друг от друга. У каждого свой статус и свой бейдж.

| Workflow | Файл | Что проверяет | Артефакты |
|---|---|---|---|
| `build` | `.github/workflows/build.yml` | Сборка Debug и Release на Windows (MSVC) и Linux (GCC 14) параллельно (матрица) | `app-Debug`, `app-Release` — `App.exe` и `config.json`; `app-linux-Debug`, `app-linux-Release` — `App` и `config.json` |
| `tests` | `.github/workflows/tests.yml` | Windows: тесты под AddressSanitizer, обычные тесты, покрытие с порогом 70%; Linux: тесты под ASan и UBSan, обычные тесты | `test-report` (также в Summary запуска), `coverage-report` — HTML-отчёт покрытия |
| `code-quality` | `.github/workflows/code-quality.yml` | Форматирование (`clang-format` 20.1.8); `clang-tidy` на Windows (MSBuild) и Linux (`compile_commands.json`) | — |
| `docs` | `.github/workflows/docs.yml` | Сборка Doxygen + MkDocs; публикация на GitHub Pages только при `push` в `master` | сайт документации |

Пакеты Conan кэшируются (`actions/cache`) по хэшу `conanfile.txt` и `profiles/`:
пока эти файлы не меняются, зависимости восстанавливаются из кэша, а не собираются заново.
Ключ кэша включает ОС раннера, поэтому у Windows и Linux кэши раздельные.

Ветка `master` защищена (`protection.json`): прямой push запрещён всем, включая
администраторов, изменения попадают только через Pull Request, и слияние возможно,
когда пройдены все обязательные проверки — `build-Debug`, `build-Release`, `tests`,
`code-quality`, `docs`, `linux-Debug`, `linux-Release`, `linux-tests`, `linux-tidy`.

```powershell
# Download the release build of the latest run
gh run download --name app-Release --dir ..\from-ci
```
