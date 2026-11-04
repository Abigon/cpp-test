# App
![build](https://github.com/Abigon/cpp-test/actions/workflows/build.yml/badge.svg)
Учебный проект курса по инженерному C++: консольное приложение App.

## Сборка и запуск

Проект использует менеджер пакетов Conan 2 и мета-систему сборки CMake. Все команды выполняются из каталога проекта (`project/`):

```powershell
# 1. Установка зависимостей через Conan и конфигурирование проекта под Debug и Release
python automation/generate_project_files.py

# 2. Сборка проекта
python automation/build_debug.py
python automation/build_release.py

# 3. Очистка проекта
python automation/clean.py

# 4. Запуск приложения (файл config.json читается из текущего каталога)
.\build\bin\Debug\App.exe
```

Параметры сборки и профили описаны в `automation/common.py`

## Архитектура проекта

Корневой `CMakeLists.txt` (решение `CppCourse`) задаёт общие настройки: стандарт C++23,
зависимости Conan, единый каталог вывода `build/bin/<Config>/`. Сборку целей он передаёт
подпроекту через `add_subdirectory(src/App)`.

```text
src/
└── App/                  # subproject App
    ├── CMakeLists.txt    # targets AppLib (STATIC) and App (executable)
    ├── Config.h          # public interface: AppConfig, parseConfig()
    ├── Config.cpp        # implementation: JSON parsing and validation
    └── main.cpp          # entry point
```

- `AppLib` — статическая библиотека со всей логикой приложения: структура `AppConfig` и функция
  `parseConfig`. Зависимость `nlohmann_json` подключена как `PRIVATE` и не видна снаружи.
- `App` — тонкий исполняемый файл: открывает `config.json`, вызывает `parseConfig`
  и выводит результат или сообщение об ошибке.

Бинарники всех подпроектов собираются в `build/bin/<Config>/`: `AppLib.lib`, `App.exe` и `AppTestRunner.exe`.

## Стиль кода

- стиль кода зафиксирован в .clang-format (на основе стиля Microsoft);
- команда автоматического исправления: `python automation/format_files.py`;
- команда проверки стиля: `python automation/format_files.py --check`;
- рекомендация включить в IDE форматирование при сохранении.

## Статический анализ

Проект защищён двумя барьерами: сборка с любым предупреждением компилятора
или анализатора не проходит ни локально, ни в CI.

**Предупреждения компилятора как ошибки.** Все цели (`AppLib`, `App`, `AppTestRunner`)
собираются со строгими флагами через функцию `set_project_warnings` из
`cmake/CompilerWarnings.cmake`:

- MSVC: `/W4 /WX /permissive-`;
- GCC/Clang: `-Wall -Wextra -Wpedantic -Werror`.

**clang-tidy.** Правила анализатора заданы в `.clang-tidy` в корне проекта
(семейства `bugprone-*`, `performance-*`, `modernize-*`, `readability-*`;
любая находка — ошибка). Запуск:

    python automation/run_tidy.py

Скрипт запускает clang-tidy через MSBuild Code Analysis: MSBuild передаёт
анализатору реальные флаги компиляции каждого файла, `compile_commands.json` не нужен.
Обычная сборка (`build_debug.py`) анализ не запускает.

## Тесты

Тесты написаны на GoogleTest и лежат в `src/App/Tests/`. Они собираются в отдельный
исполняемый файл `AppTestRunner`, который линкуется с той же библиотекой `AppLib`,
что и приложение.

Что проверяется — разбор конфигурационного файла функцией `parseConfig`:

- корректный JSON читается в `AppConfig` (заголовок, ширина и высота окна);
- при отсутствии ключа выбрасывается `std::runtime_error`, и в сообщении указано имя ключа;
- при неверном типе значения выбрасывается `std::runtime_error`;
- при синтаксически невалидном JSON выбрасывается `std::runtime_error`.

Запуск:

```powershell
# Сборка Debug и запуск всех тестов через CTest (отчёт: build/test-report.xml)
python automation/run_tests.py

# Прямой запуск тестового раннера после сборки
.\build\bin\Debug\AppTestRunner.exe
```

### Покрытие кода

Покрытие измеряется утилитой [OpenCppCoverage](https://github.com/OpenCppCoverage/OpenCppCoverage)
(установка: `winget install OpenCppCoverage.OpenCppCoverage`). Пересобирать проект
со специальными флагами не нужно: используется обычная Debug-сборка и её `.pdb`.

```powershell
# Сборка Debug, запуск тестов под OpenCppCoverage и сводная таблица по файлам
python automation/run_coverage.py

# То же, но с ошибкой, если общее покрытие ниже порога
python automation/run_coverage.py --min 70
```

Отчёты:

- `build/coverage/html/index.html` — интерактивный HTML-отчёт: выполненные строки
  подсвечены зелёным, невыполненные — красным;
- `build/coverage/coverage.xml` — отчёт в формате Cobertura XML для CI.

В CI покрытие проверяется с порогом **70%**: если оно опустится ниже, сборка упадёт.
Порог защищает от деградации и не требует 100% — недостижимые строки
(скобки после `throw`) не покрываются никогда.

## AddressSanitizer

AddressSanitizer (ASan) находит ошибки памяти во время выполнения: выход за границы
буфера, обращение к освобождённой памяти, повторное освобождение. Компилятор
добавляет проверку к каждому обращению к памяти, и при недопустимом доступе программа
сразу останавливается с отчётом: тип ошибки, строка с ошибкой и место, где был
выделен буфер.

Инструментированная сборка работает медленнее и требует больше памяти, поэтому она
вынесена в отдельный каталог `build-asan/` и не смешивается с обычной сборкой в `build/`.
Включается она опцией CMake `ENABLE_ASAN` (по умолчанию `OFF`) из модуля
`cmake/Sanitizers.cmake`; функция `enable_sanitizers` применяется ко всем целям
(`AppLib`, `App`, `AppTestRunner`). Файл тулчейна Conan берётся общий, из `build/`.

Запуск:

```powershell
# Сборка в build-asan/ и запуск всех тестов под AddressSanitizer
python automation/run_asan.py
```

Особенности сборки на MSVC:

- флаг `/RTC1` убирается из Debug-флагов: он несовместим с `/fsanitize=address`;
- задан `_DISABLE_STL_ANNOTATION`: GoogleTest из Conan собран без ASan, и без этого
  определения компоновка завершается ошибкой `LNK2038`;
- рантайм `clang_rt.asan_dynamic-x86_64.dll` копируется рядом с каждым исполняемым
  файлом после сборки, поэтому тесты запускаются из любой консоли.

Для работы нужен компонент Visual Studio «C++ AddressSanitizer».

В CI шаг `Tests under AddressSanitizer` выполняется сразу после `Build Debug` и до
`Run tests`. При ошибке памяти запуск сразу падает с отчётом ASan в логе. Если бы первыми
шли обычные тесты, Debug-сборка открыла бы окно отладочной кучи, и раннер
завис бы до тайм-аута.

## Непрерывная интеграция (CI)

Сборка проекта автоматизирована через GitHub Actions: сценарий `.github/workflows/build.yml`
запускается на чистой виртуальной машине `windows-latest` при каждом `push` и Pull Request.

Шаги сценария:

- установка Conan 2 и `clang-format` фиксированной версии (той же, что используется локально);
- генерация зависимостей и файлов проекта: `python automation/generate_project_files.py`;
- сборка конфигураций Debug и Release: `python automation/build_debug.py`, `python automation/build_release.py`;
- тесты под AddressSanitizer: `python automation/run_asan.py` — выполняется до обычных тестов, сборка падает при любой ошибке памяти;
- запуск тестов: `python automation/run_tests.py`; отчёт публикуется в Summary запуска и сохраняется артефактом `test-report`;
- измерение покрытия: `python automation/run_coverage.py --min 70` — сборка падает, если покрытие ниже 70%; таблица публикуется в Summary запуска, HTML-отчёт сохраняется артефактом `coverage-report`;
- проверка стиля кода: `python automation/format_files.py --check` — сборка падает, если код не отформатирован;
- статический анализ: `python automation/run_tidy.py` — сборка падает при любой находке clang-tidy.

Профили Conan в `profiles/` определяют версию компилятора автоматически (`detect_api`),
поэтому одни и те же профили работают и локально, и на CI.

### Готовая сборка

Каждый успешный запуск публикует артефакт `app-release`: `build/bin/Release/App.exe` и `config.json`.
Скачать его можно на странице запуска во вкладке **Actions** или командой:

```powershell
gh run download --name app-release --dir ..\from-ci
cd ..\from-ci
.\build\bin\Release\App.exe
```