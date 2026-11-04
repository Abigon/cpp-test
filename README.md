# App

[![build](https://github.com/Abigon/cpp-test/actions/workflows/build.yml/badge.svg)](https://github.com/Abigon/cpp-test/actions/workflows/build.yml)

Учебный проект курса «Инженерный C++»: консольное приложение `App`, которое читает
настройки из `config.json` и выводит их. Логика вынесена в статическую библиотеку
`AppLib` и покрыта юнит-тестами; сборка, тесты и проверки качества автоматизированы
скриптами Python и выполняются в GitHub Actions.

## Системные требования

- Windows 10/11 (x64);
- Visual Studio 2022 или новее с компонентами «Разработка классических приложений на C++»
  и «C++ AddressSanitizer»;
- CMake 3.25+;
- Python 3;
- Conan 2 (`pip install conan`);
- OpenCppCoverage — для измерения покрытия;
- для сборки документации — Doxygen и пакеты из `requirements-docs.txt`.

## Сборка и запуск

Все команды выполняются из корня проекта:

```powershell
# 1. Install Conan dependencies and configure CMake (Debug and Release)
python automation/generate_project_files.py

# 2. Build the Debug configuration
python automation/build_debug.py

# 3. Run the app (config.json is read from the current directory)
.\build\bin\Debug\App.exe
```

- Release-сборка: `python automation/build_release.py`, бинарник — `build\bin\Release\App.exe`.
- Полная очистка артефактов сборки: `python automation/clean.py`
  (`--dry-run` — только показать, что будет удалено).
- Общие пути, конфигурации и профили Conan для всех скриптов заданы в `automation/common.py`.

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

## Структура проекта

```text
project/
├── .github/workflows/   # CI pipeline (build.yml)
├── automation/          # Python scripts: generate, build, test, check, clean
├── cmake/               # CMake modules: warnings, sanitizers, clang-format
├── profiles/            # Conan profiles for Debug and Release
├── src/App/             # subproject: AppLib, App and their sources
│   └── Tests/           # GoogleTest tests -> AppTestRunner
├── CMakeLists.txt       # root project: C++23, dependencies, output dir
├── conanfile.txt        # dependencies: nlohmann_json, gtest
└── config.json          # app configuration read at startup
```

Бинарники всех целей собираются в `build/bin/<Config>/`.

## Непрерывная интеграция (CI)

Сценарий `.github/workflows/build.yml` запускается на `windows-latest` при каждом
`push` и Pull Request: генерация проекта, сборка Debug, тесты под AddressSanitizer,
обычные тесты, покрытие с порогом 70%, сборка Release, проверка форматирования и
статический анализ. Любой упавший шаг делает запуск красным.

Артефакты запуска:

- `app-release` — `App.exe` и `config.json` из Release-сборки;
- `test-report` — отчёт тестов (также публикуется в Summary запуска);
- `coverage-report` — HTML-отчёт покрытия.

```powershell
# Download the release build of the latest run
gh run download --name app-release --dir ..\from-ci
```
