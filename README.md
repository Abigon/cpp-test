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
.\build\Debug\app.exe
```

Параметры сборки и профили описаны в `automation/common.py`

## Стиль кода

- стиль кода зафиксирован в .clang-format (на основе стиля Microsoft);
- команда автоматического исправления: `python automation/format_files.py`;
- команда проверки стиля: `python automation/format_files.py --check`;
- рекомендация включить в IDE форматирование при сохранении.

## Непрерывная интеграция (CI)

Сборка проекта автоматизирована через GitHub Actions: сценарий `.github/workflows/build.yml`
запускается на чистой виртуальной машине `windows-latest` при каждом `push` и Pull Request.

Шаги сценария:

- установка Conan 2 и `clang-format` фиксированной версии (той же, что используется локально);
- генерация зависимостей и файлов проекта: `python automation/generate_project_files.py`;
- сборка конфигураций Debug и Release: `python automation/build_debug.py`, `python automation/build_release.py`;
- проверка стиля кода: `python automation/format_files.py --check` — сборка падает, если код не отформатирован.

Профили Conan в `profiles/` определяют версию компилятора автоматически (`detect_api`),
поэтому одни и те же профили работают и локально, и на CI.

### Готовая сборка

Каждый успешный запуск публикует артефакт `app-release`: `build/Release/app.exe` и `config.json`.
Скачать его можно на странице запуска во вкладке **Act или командой:

```powershell
gh run download --name app-release --dir ..\from-ci
cd ..\from-ci
.\build\Release\app.exe
```