# Разработка

Все операции с проектом выполняются скриптами из `automation/`. Скрипты можно
запускать из любого каталога: пути вычисляются от расположения `common.py`.

## Windows и Linux

Скрипты одни и те же на обеих платформах: на Windows они запускаются командой
`python`, на Linux (в том числе в WSL) — `python3`. Все различия платформ собраны
в `common.py`, остальные скрипты о платформе не знают.

| | Windows (MSVC) | Linux (GCC 14) |
|---|---|---|
| Профили Conan | `profiles/windows-msvc-*` | `profiles/linux-gcc-*` |
| Каталог сборки | `build/` — общий для Debug и Release | `build/Debug/`, `build/Release/` — свой на конфигурацию |
| Бинарники | `build/bin/<Config>/` | `build/<Config>/bin/` |
| Сборка под санитайзерами | `build-asan/` | `build-asan/Debug/` |

Причина разных каталогов — генераторы CMake. Генератор Visual Studio
многоконфигурационный: Debug и Release живут в одном каталоге, а конфигурация
выбирается при сборке (`--config`). Генератор Makefile одноконфигурационный:
конфигурация задаётся при конфигурировании (`CMAKE_BUILD_TYPE`), поэтому у каждой
свой каталог. Раздельные каталоги нужны и на одной машине: `CMakeCache.txt` хранит
абсолютные пути, а WSL видит тот же диск по другому пути (`/mnt/...`).

## Скрипты автоматизации

| Скрипт | Что делает |
|---|---|
| `common.py` | общие функции и пути: платформа, каталоги сборки, профили Conan, конфигурации |
| `generate_project_files.py` | ставит зависимости Conan для Debug и Release и конфигурирует CMake |
| `build_debug.py` | собирает Debug (при необходимости сначала генерирует проект) |
| `build_release.py` | собирает Release |
| `clean.py` | удаляет всё, что перечислено в `.gitignore`; `--dry-run` — только показать |
| `run_tests.py` | собирает Debug и запускает тесты через CTest, отчёт `test-report.xml` в каталоге сборки Debug |
| `run_coverage.py` | покрытие через OpenCppCoverage; `--min 70` — ошибка при покрытии ниже порога; на Linux пропускается |
| `run_asan.py` | отдельная сборка под санитайзерами и тесты: на Windows — AddressSanitizer, на Linux — ASan и UBSan |
| `format_files.py` | форматирует код clang-format; `--check` — только проверка |
| `run_tidy.py` | статический анализ clang-tidy: на Windows через MSBuild Code Analysis, на Linux через `compile_commands.json` |
| `build_docs.py` | сборка документации |

## Перед коммитом

```powershell
python automation/format_files.py      # format sources
python automation/run_tests.py         # unit tests
python automation/run_asan.py          # tests under sanitizers
python automation/run_tidy.py          # static analysis
git diff                               # review your own changes
```

На Linux — те же команды с `python3`. Сборка на втором компиляторе находит
предупреждения, которые не видит первый, поэтому перед Pull Request полезно
прогнать проверки на обеих платформах.

В коммит добавляются только нужные файлы, по имени: `git add <файл> <файл>`.
CI выполняет те же проверки; локальный прогон экономит время на красных запусках.

## Документация

Документация собирается из двух источников:

- **Справочник API** — Doxygen генерирует HTML в `docs/api` из комментариев `///`
  в заголовочных файлах `src/App`. Конфигурация — `Doxyfile`. Недокументированная
  публичная сущность — ошибка (`WARN_AS_ERROR`).
- **Страницы проекта** — Markdown-файлы в `docs/`, MkDocs с темой Material собирает
  из них сайт в `build/docs/site`. Конфигурация — `mkdocs.yml`, версии пакетов
  зафиксированы в `requirements-docs.txt`. Битая ссылка — ошибка (`--strict`).

Каталог `docs/api` генерируется и в репозиторий не попадает (`.gitignore`).
