# App

Учебный проект курса «Инженерный C++»: консольное приложение `App`, которое читает
настройки окна из `config.json` и выводит их.

Проект показывает инженерную инфраструктуру C++-проекта целиком: Modern CMake,
зависимости через Conan 2, юнит-тесты на GoogleTest, покрытие, AddressSanitizer,
clang-format, clang-tidy и CI в GitHub Actions. Вся логика вынесена в статическую
библиотеку `AppLib`, поэтому её можно тестировать отдельно от исполняемого файла.

## Быстрый старт

Из корня проекта:

```powershell
# 1. Install Conan dependencies and configure CMake (Debug and Release)
python automation/generate_project_files.py

# 2. Build the Debug configuration
python automation/build_debug.py

# 3. Run the app (config.json is read from the current directory)
.\build\bin\Debug\App.exe
```

Ожидаемый вывод:

```text
Hello, App! Window: 800x600
```

Системные требования и полный список команд — в `README.md` в корне репозитория.

## Разделы

- [Архитектура](architecture.md) — сборочные цели, модель конфигурации, модули CMake.
- [Разработка](development.md) — скрипты автоматизации, чек-лист перед коммитом,
  сборка документации.
- [Справочник API](api/index.html) — описание публичного интерфейса `AppLib`,
  сгенерированное Doxygen из комментариев `///` в заголовочных файлах.
