# App

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
