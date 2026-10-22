# App

Учебный проект курса по инженерному C++: консольное приложение App.

## Сборка и запуск

Проект использует менеджер пакетов Conan 2 и мета-систему сборки CMake. Все команды выполняются из каталога проекта (`project/`):

```powershell
# 1. Установка зависимостей через Conan под Debug и Release
conan install . --output-folder=build -pr:h profiles/windows-msvc-debug -pr:b profiles/windows-msvc-debug --build=missing
conan install . --output-folder=build -pr:h profiles/windows-msvc-release -pr:b profiles/windows-msvc-release --build=missing

# 2. Конфигурирование с тулчейном Conan
cmake -S . -B build "-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake"

# 3. Сборка проекта
cmake --build build --config Debug

# 4. Запуск приложения (файл config.json читается из текущего каталога)
.\build\Debug\app.exe
```