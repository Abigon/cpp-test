# Каркас проекта: спецификация

Техническое задание на создание нового проекта C++ с нуля (скилл `new-cpp-project`)
и контрольный список для ревью. Имя проекта задаётся при генерации и ниже
обозначено `<Name>`; владелец и репозиторий GitHub — `<owner>` и `<repo>`.
Спецификация самодостаточна: чего здесь нет, того в проекте быть не должно.
Критерий приёмки — раздел 11.

## 1. Структура каталогов

```text
<target>/
├── CMakeLists.txt                # root: project(<Name>), C++23, modules, add_subdirectory(src/<Name>)
├── conanfile.txt                 # nlohmann_json/3.12.0, gtest/1.18.0
├── config.json                   # {"title": "<Name>", "window": {"width": 800, "height": 600}}
├── README.md                     # section 9
├── .gitignore                    # see below
├── .clang-format                 # section 5
├── .clang-tidy                   # section 6
├── Doxyfile                      # section 8
├── mkdocs.yml                    # section 8
├── requirements-docs.txt         # section 8
├── protection.json               # section 10
├── docs/                         # index.md, architecture.md, development.md
├── profiles/                     # windows-msvc-debug, windows-msvc-release, linux-gcc-debug, linux-gcc-release
├── cmake/                        # CompilerWarnings.cmake, Sanitizers.cmake, ClangFormat.cmake
├── automation/                   # section 4
├── src/<Name>/                   # CMakeLists.txt, Config.h, Config.cpp, main.cpp
│   └── Tests/ConfigTest.cpp      # directory name exactly "Tests"
└── .github/workflows/            # build.yml, tests.yml, code-quality.yml, docs.yml
```

`docs/`: `index.md` — обзор и быстрый старт; `architecture.md` — цели, модель
конфигурации, модули CMake (каталог вывода — для обеих платформ или ссылкой на таблицу из `development.md`); `development.md` — скрипты, платформы, чек-лист перед коммитом.

`.gitignore` — ровно эти строки: `build/`, `.vs/`, `build-asan/`, `docs/api/`,
`CMakeUserPresets.json`, `__pycache__/`, `LastCoverageResults.log`.

## 2. Сборка

- Корневой `CMakeLists.txt`, порядок строк: `cmake_minimum_required(VERSION 3.25)`;
  `project(<Name> LANGUAGES CXX)`; `set(CMAKE_CXX_STANDARD 23)`;
  `set(CMAKE_CXX_STANDARD_REQUIRED ON)`; `find_package(nlohmann_json REQUIRED)`;
  `find_package(GTest REQUIRED)`; `enable_testing()`;
  `set_property(GLOBAL PROPERTY USE_FOLDERS ON)`; `CMAKE_RUNTIME_OUTPUT_DIRECTORY` и
  `CMAKE_ARCHIVE_OUTPUT_DIRECTORY` = `${CMAKE_BINARY_DIR}/bin`;
  `include(cmake/CompilerWarnings.cmake)`; `include(cmake/Sanitizers.cmake)`;
  `add_subdirectory(src/<Name>)`; `set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT <Name>)`;
  `include(cmake/ClangFormat.cmake)` — последней строкой.
- `src/<Name>/CMakeLists.txt`: `project(<Name> LANGUAGES CXX)`; имена целей только через
  `${PROJECT_NAME}`:
  - `<Name>Lib` — `STATIC`, файлы `Config.cpp`, `Config.h`;
    `target_include_directories(... PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})`;
    `nlohmann_json::nlohmann_json` — `PRIVATE`;
  - `<Name>` — исполняемый файл только из `main.cpp`, линкует `<Name>Lib` `PRIVATE`;
    `VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"`;
  - `<Name>TestRunner` — из `Tests/ConfigTest.cpp`, линкует `<Name>Lib` и `GTest::gtest_main`;
    `include(GoogleTest)`, `gtest_discover_tests(<Name>TestRunner DISCOVERY_TIMEOUT 30)`;
  - у всех трёх целей `FOLDER <Name>`, вызовы `set_project_warnings(...)` и `enable_sanitizers(...)`.
- `cmake/CompilerWarnings.cmake`: функция `set_project_warnings(target)`, `PRIVATE`:
  MSVC — `/W4 /WX /permissive-`; иначе — `-Wall -Wextra -Wpedantic -Werror`.
- `conanfile.txt`: `[requires]` `nlohmann_json/3.12.0`, `gtest/1.18.0`;
  `[generators]` `CMakeDeps`, `CMakeToolchain`.
- Профили Conan (`[settings]`, все `arch=x86_64`, `compiler.cppstd=23`):
  - `windows-msvc-debug` / `windows-msvc-release`: первая строка
    `{% set compiler, version, compiler_exe = detect_api.detect_default_compiler() %}`;
    `compiler={{ compiler }}`, `compiler.version={{ version }}`, `compiler.runtime=dynamic`,
    `compiler.runtime_type=Debug|Release`, `build_type=Debug|Release`, `os=Windows`;
  - `linux-gcc-debug` / `linux-gcc-release`: `compiler=gcc`, `compiler.version=14`,
    `compiler.libcxx=libstdc++11`, `build_type=Debug|Release`, `os=Linux`;
    `[conf]` `tools.build:compiler_executables={"c": "gcc-14", "cpp": "g++-14"}`.
- Каталоги сборки: Windows (генератор Visual Studio) — один `build/` для Debug и Release,
  бинарники в `build/bin/<Config>/`; Linux (Makefiles) — `build/<Config>/`, бинарники
  в `build/<Config>/bin/`.

## 3. Исходный код

- Пространство имён `LifeExe`. Типы — PascalCase, функции — camelCase.
- `Config.h`: `#pragma once`; `struct AppConfig { std::string title; int width{0}; int height{0}; }`;
  `AppConfig parseConfig(std::istream& input);`. Документация `///`: namespace, struct,
  каждое поле `///<`, функция с `@param`, `@return`, `@throws`, `@note`.
- `Config.cpp`: функция `require(object, std::string_view key)` в анонимном namespace;
  отсутствующий ключ — `std::runtime_error` с текстом `config: key '<key>' is missing`;
  `parse_error` → `config: invalid JSON: ...`; `type_error` → `config: wrong value type: ...`;
  значения через `.get<T>()`, сообщения через `std::format`; локальные переменные объявляются
  ровно как `nlohmann::json json;` и `AppConfig config;` (без `{}`).
- `main.cpp`: открывает `config.json` из текущего каталога; нет файла — сообщение в `stderr`
  и `EXIT_FAILURE`; успех — `std::println("Hello, {}! Window: {}x{}", ...)`, `EXIT_SUCCESS`.
  Тело в `try`; `catch (const std::exception&)` и `catch (...)` выводят только через `std::fputs`.
- `Tests/ConfigTest.cpp`: GoogleTest, набор `ConfigTest`, ровно четыре теста:
  `ShouldReadTitleAndWindow`, `ShouldNameMissingKey`, `ShouldRejectWrongValueType`,
  `ShouldRejectInvalidJson`; вход — `std::istringstream` с raw-строкой JSON. `ShouldNameMissingKey`:
  вход `{"title": "<Name>", "window": {"height": 600}}` (нет `width`), проверка
  `EXPECT_NE(std::string{e.what()}.find("width"), std::string::npos)` внутри `catch (const std::runtime_error& e)`.
- Комментарии в коде — на английском.

## 4. Скрипты автоматизации

`automation/`, Python 3, только стандартная библиотека. Запуск из любого каталога: пути
вычисляются от файла. `common.py` — единственное место с различиями платформ:
`PROJECT_ROOT`, `PROJECT_NAME = "<Name>"` (единственное место имени проекта в `automation/`),
`IS_WINDOWS`, `CONFIGURATIONS = ("Debug", "Release")`, `run(command)`
(печатает `+ <команда>`, выходит с кодом ошибки), `profile(configuration)`,
`build_dir(configuration, root="build")`, `bin_dir(configuration)`, `toolchain(...)`,
`relative(path)`, `conan_install(...)` (`--output-folder`, `-pr:h` и `-pr:b` одним профилем,
`--build=missing`), `configure(...)` (`-DCMAKE_TOOLCHAIN_FILE`; на Linux ещё
`-DCMAKE_BUILD_TYPE` и `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`), `ensure_generated(...)`,
`cmake_build(...)` (`--config` только на Windows), `build(configuration)`.

| Скрипт | Поведение |
|---|---|
| `generate_project_files.py` | `conan install` для Debug и Release; CMake: Windows — один раз, Linux — на каждую конфигурацию |
| `build_debug.py`, `build_release.py` | `build("Debug")` / `build("Release")` |
| `run_tests.py` | сборка Debug, `ctest --test-dir <build> -C Debug --output-on-failure --output-junit test-report.xml` |
| `run_coverage.py` | Windows: OpenCppCoverage (`PATH` или `C:\Program Files\OpenCppCoverage`) запускает `bin_dir("Debug") / f"{PROJECT_NAME}TestRunner.exe"`, `--sources src/{PROJECT_NAME}`, `--excluded_sources *\Tests\*`, HTML в `build/coverage/html`, Cobertura `build/coverage/coverage.xml`, таблица в консоль и в `GITHUB_STEP_SUMMARY`, `--min N`; Linux (`if not IS_WINDOWS`): сообщение ровно `coverage is measured on Windows only, skipping` и код 0 |
| `run_tidy.py` | Windows: `cmake --build build --config Debug -- /p:RunCodeAnalysis=true /p:EnableClangTidyCodeAnalysis=true /p:EnableMicrosoftCodeAnalysis=false`; Linux: сборка Debug, затем `clang-tidy -p build/Debug` по всем `src/**/*.cpp` |
| `run_asan.py` | каталог задаётся буквально выражением `build_dir("Debug", root="build-asan")` (без вынесения в константу), `-DENABLE_ASAN=ON`, сборка Debug, `ctest -C Debug --output-on-failure` |
| `format_files.py` | цель `format`; с `--check` — `format-check` |
| `build_docs.py` | `doxygen Doxyfile`, затем `python -m mkdocs build --strict`; `--serve` — `mkdocs serve` |
| `clean.py` | `git clean -Xdn` для показа, `git clean -Xdf` для удаления; `--dry-run` |

## 5. Форматирование

`.clang-format` целиком:

```yaml
BasedOnStyle: Microsoft
IndentWidth: 4
UseTab: Never
TabWidth: 4
BreakBeforeBraces: Allman
ColumnLimit: 140
AccessModifierOffset: -4
SortIncludes: false
AllowShortBlocksOnASingleLine: false
AlignAfterOpenBracket: DontAlign
AllowShortFunctionsOnASingleLine: Inline
PointerAlignment: Left
AllowShortIfStatementsOnASingleLine: true
SpacesBeforeTrailingComments: 2
AllowShortCaseLabelsOnASingleLine: true
IndentCaseLabels: true
AlwaysBreakTemplateDeclarations: Yes
```

`cmake/ClangFormat.cmake`: `find_program(CLANG_FORMAT_EXE NAMES clang-format)` сначала по `PATH`,
затем с `HINTS` из `C:/Program Files/Microsoft Visual Studio/*/*/VC/Tools/Llvm/bin` и `.../Llvm/x64/bin`;
не найден — `message(WARNING ...)` и `return()`; найден — `message(STATUS "clang-format: ${CLANG_FORMAT_EXE}")`
(строка `-- clang-format: <путь>` обязательна в выводе конфигурирования). `file(GLOB_RECURSE ... CONFIGURE_DEPENDS)` по
`src/*.cpp`, `src/*.h`; цели `format` (`-i`) и `format-check` (`--dry-run --Werror`).

## 6. Статический анализ

`.clang-tidy` целиком:

```yaml
Checks: '-*,bugprone-*,performance-*,modernize-*,-modernize-use-trailing-return-type,readability-*,-readability-magic-numbers,-readability-identifier-length,-readability-uppercase-literal-suffix,misc-const-correctness'
WarningsAsErrors: '*'
HeaderFilterRegex: 'src[/\\]<Name>[/\\].*'
FormatStyle: file
```

## 7. Санитайзеры

`cmake/Sanitizers.cmake`: `option(ENABLE_ASAN "Build with AddressSanitizer (plus UBSan on GCC/Clang)" OFF)`;
имя опции фиксировано: на MSVC она включает ASan, на GCC/Clang — ASan и UBSan.
- MSVC при `ENABLE_ASAN`: удалить `/RTC1` из `CMAKE_CXX_FLAGS_DEBUG`; `ASAN_RUNTIME_DLL` =
  `<каталог компилятора>/clang_rt.asan_dynamic-x86_64.dll`, нет файла — `FATAL_ERROR`
  с указанием компонента «C++ AddressSanitizer».
- Функция `enable_sanitizers(target)` (без `ENABLE_ASAN` — `return()`):
  - MSVC: `/fsanitize=address`, `_DISABLE_STL_ANNOTATION`, `/INCREMENTAL:NO`; для
    `EXECUTABLE` — `POST_BUILD` `copy_if_different` DLL в `$<TARGET_FILE_DIR:target>`;
  - иначе: компиляция `-fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer`,
    линковка `-fsanitize=address,undefined`.

## 8. Документация

`Doxyfile` — только эти ключи: `PROJECT_NAME = <Name>`,
`PROJECT_BRIEF = "Application logic library and executable"`, `OUTPUT_DIRECTORY = docs`,
`INPUT = src/<Name>`, `FILE_PATTERNS = *.h`, `RECURSIVE = NO`, `EXCLUDE = src/<Name>/Tests`,
`EXTRACT_ALL = NO`, `WARN_IF_UNDOCUMENTED = YES`, `WARN_AS_ERROR = FAIL_ON_WARNINGS`, `QUIET = YES`,
`GENERATE_HTML = YES`, `HTML_OUTPUT = api`, `GENERATE_LATEX = NO`, `HAVE_DOT = NO`,
`JAVADOC_AUTOBRIEF = YES`.

`requirements-docs.txt`: `mkdocs==1.6.1`, `mkdocs-material==9.7.7`.

`mkdocs.yml`: `site_name: <Name>`, `site_description: Документация проекта <Name>`, `docs_dir: docs`,
`site_dir: build/docs/site`, `theme: name: material, language: ru`;
`nav`: `Обзор: index.md`, `Архитектура: architecture.md`, `Разработка: development.md`,
`Справочник API: api/index.html`; `markdown_extensions`: `admonition`, `pymdownx.superfences`.
Страницы `docs/*.md` — на русском.

## 9. README

`README.md` на русском, разделы в порядке: `# <Name>` и четыре значка workflow
(`https://github.com/<owner>/<repo>/actions/workflows/<file>.yml/badge.svg`); описание в
два-три предложения; «Системные требования» (Windows; Linux Ubuntu 24.04/WSL с командой
`sudo apt install -y g++-14 cmake make clang-tidy clang-format pipx`); «Сборка и
запуск» (`generate_project_files.py`, `build_debug.py`, запуск бинарника; Windows `python`,
Linux `python3`; `build_release.py`, `clean.py`, `common.py`); «Тестирование» (`run_tests.py`,
`run_coverage.py --min 70`, `run_asan.py`); «Контроль качества кода»
(`format_files.py --check`, `run_tidy.py`; флаги предупреждений обоих компиляторов: MSVC `/W4 /WX /permissive-`,
GCC `-Wall -Wextra -Wpedantic -Werror`); «Документация» (адрес
`https://<owner>.github.io/<repo>/`, `build_docs.py`, `--serve`); «Структура проекта» (дерево каталогов; названы цели `<Name>Lib`, `<Name>`, `<Name>TestRunner`
и каталоги бинарников `build/bin/<Config>/` и `build/<Config>/bin/`);
«Непрерывная интеграция (CI)» — таблица workflow с артефактами, кэш Conan, защита `master`;
раннеры указываются для каждого workflow по таблице раздела 10, без обобщений «все на обеих ОС».

## 10. CI/CD

Четыре workflow, поле `name:` совпадает с именем файла: `build`, `tests`, `code-quality`, `docs`;
у каждого `on: push: branches: [master]` и `pull_request`,
`concurrency.group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`
(у `docs` — `false`). Кэш `actions/cache@v6`, путь `~/.conan2/p`, ключ
`conan-${{ runner.os }}-${{ hashFiles('conanfile.txt', 'profiles/**') }}`. Действия:
`actions/checkout@v7`, `actions/upload-artifact@v7`, `actions/upload-pages-artifact@v5`,
`actions/deploy-pages@v5`, `phoenix-actions/test-reporting@v16`. Windows — `pip install conan`,
`python`; Linux — `sudo apt-get update`, затем `sudo apt-get install -y g++-14`, `pipx install conan`, `python3`.
Версия Conan не закрепляется (последняя Conan 2); `clang-format` закреплён: от его версии
зависит результат форматирования.

| Файл | Работа (`name`) | Раннер | Шаги |
|---|---|---|---|
| `build.yml` | `build-Debug`, `build-Release` (матрица `include`: `configuration: Debug`, `script: build_debug.py` и `configuration: Release`, `script: build_release.py`; `fail-fast: false`) | `windows-latest` | generate, `python automation/${{ matrix.script }}`; артефакт `app-<Config>`: `build/bin/<Config>/<Name>.exe`, `config.json` |
| `build.yml` | `linux-Debug`, `linux-Release` (та же матрица `include`) | `ubuntu-latest` | generate, `python3 automation/${{ matrix.script }}`; артефакт `app-linux-<Config>`: `build/<Config>/bin/<Name>`, `config.json` |
| `tests.yml` | `tests` | `windows-latest` | `run_asan.py`, `run_tests.py`, `choco install opencppcoverage`, `run_coverage.py --min 70`; артефакты `coverage-report` (путь `build/coverage/html`), `test-report` (путь `build/test-report.xml`), оба `if: always()`; отчёт `java-junit` в step summary |
| `tests.yml` | `linux-tests` | `ubuntu-latest` | `run_asan.py`, `run_tests.py` |
| `code-quality.yml` | `code-quality` | `windows-latest` | `pip install clang-format==20.1.8` + каталог scripts в `GITHUB_PATH`; generate; `format_files.py --check`; `run_tidy.py` |
| `code-quality.yml` | `linux-tidy` | `ubuntu-latest` | `sudo apt-get update`, `sudo apt-get install -y g++-14 clang-tidy`; generate; `run_tidy.py` |
| `docs.yml` | `docs` | `windows-latest` | `choco install doxygen.install`, `pip install -r requirements-docs.txt`, `build_docs.py`, Pages-артефакт `build/docs/site` |
| `docs.yml` | `deploy` | `ubuntu-latest` | `needs: docs`, только push в ветку по умолчанию; `pages: write`, `id-token: write`, `environment: github-pages` |

`protection.json`: `required_status_checks.strict: false`, `contexts` — `build-Debug`,
`build-Release`, `tests`, `code-quality`, `docs`, `linux-Debug`, `linux-Release`,
`linux-tests`, `linux-tidy`; `enforce_admins: true`; `required_pull_request_reviews: null`;
`restrictions: null`.

## 11. Критерии приёмки

Из корня репозитория курса:

```powershell
python checks/scaffold.py <каталог проекта> --report reports/scaffold-report.txt
```

Все проверки спринтов `cpp-engineering` 04–14 — `[OK  ]`. Внутренняя самопроверка генератора:
`generate_project_files.py`, `build_debug.py`, `run_tests.py`, `format_files.py --check`,
`run_tidy.py`, `run_asan.py`, `build_docs.py` завершаются с кодом 0; `<Name>` печатает
`Hello, <Name>! Window: 800x600`. Расхождение исправляется в этой спецификации, а не в
сгенерированных файлах.
