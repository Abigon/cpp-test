# Архитектура

Корневой `CMakeLists.txt` задаёт общие настройки: стандарт C++23, зависимости Conan
(`nlohmann_json`, `GTest`), единый каталог вывода `build/bin/<Config>/` и подключение
модулей из `cmake/`. Сборочные цели описаны в подпроекте `src/App`
(`add_subdirectory(src/App)`).

## Сборочные цели

| Цель | Тип | Исходные файлы | Назначение |
|---|---|---|---|
| `AppLib` | статическая библиотека | `Config.h`, `Config.cpp` | вся логика: `AppConfig` и `parseConfig` |
| `App` | исполняемый файл | `main.cpp` | открывает `config.json`, вызывает `parseConfig`, выводит результат |
| `AppTestRunner` | исполняемый файл | `Tests/ConfigTest.cpp` | юнит-тесты GoogleTest, `main()` из `gtest_main` |

`App` и `AppTestRunner` линкуются с одной и той же `AppLib`: тесты проверяют
тот же код, что выполняется в приложении. Зависимость `nlohmann_json` подключена
к `AppLib` как `PRIVATE` и не видна целям, которые используют библиотеку.

## Конфигурация

Функция `parseConfig` читает JSON из `std::istream`, а не из файла по имени:

- приложение передаёт ей `std::ifstream` с `config.json`;
- тесты передают `std::istringstream` со строкой JSON и не зависят от файловой системы.

Формат:

```json
{
  "title": "App",
  "window": { "width": 800, "height": 600 }
}
```

Ошибки передаются исключением `std::runtime_error`: невалидный JSON, отсутствующий
ключ (имя ключа есть в сообщении) или значение неверного типа. `main()` перехватывает
исключение, выводит сообщение в `stderr` и возвращает `EXIT_FAILURE`.

## Модули CMake

| Модуль | Что делает |
|---|---|
| `cmake/CompilerWarnings.cmake` | функция `set_project_warnings`: MSVC `/W4 /WX /permissive-`, GCC/Clang `-Wall -Wextra -Wpedantic -Werror` |
| `cmake/Sanitizers.cmake` | опция `ENABLE_ASAN` (по умолчанию `OFF`) и функция `enable_sanitizers` |
| `cmake/ClangFormat.cmake` | цели `format` и `format-check`; clang-format ищется сначала в `PATH`, затем в Visual Studio |

Особенности ASan на MSVC в `Sanitizers.cmake`:

- флаг `/RTC1` удаляется из Debug-флагов: он несовместим с `/fsanitize=address`;
- задан `_DISABLE_STL_ANNOTATION`: GoogleTest из Conan собран без ASan, и без
  этого определения компоновка завершается ошибкой `LNK2038`;
- `clang_rt.asan_dynamic-x86_64.dll` копируется рядом с каждым исполняемым файлом
  на этапе `POST_BUILD`, поэтому тесты запускаются из любой консоли.
