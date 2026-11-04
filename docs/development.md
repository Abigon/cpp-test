# Разработка

Все операции с проектом выполняются скриптами из `automation/`. Скрипты можно
запускать из любого каталога: пути вычисляются от расположения `common.py`.

## Скрипты автоматизации

| Скрипт | Что делает |
|---|---|
| `common.py` | общие функции и пути: каталог сборки, профили Conan, конфигурации |
| `generate_project_files.py` | ставит зависимости Conan для Debug и Release и конфигурирует CMake |
| `build_debug.py` | собирает Debug (при необходимости сначала генерирует проект) |
| `build_release.py` | собирает Release |
| `clean.py` | удаляет всё, что перечислено в `.gitignore`; `--dry-run` — только показать |
| `run_tests.py` | собирает Debug и запускает тесты через CTest, отчёт `build/test-report.xml` |
| `run_coverage.py` | покрытие через OpenCppCoverage; `--min 70` — ошибка при покрытии ниже порога |
| `run_asan.py` | отдельная сборка в `build-asan/` и тесты под AddressSanitizer |
| `format_files.py` | форматирует код clang-format; `--check` — только проверка |
| `run_tidy.py` | статический анализ clang-tidy через MSBuild Code Analysis |
| `build_docs.py` | сборка документации |

## Перед коммитом

```powershell
python automation/format_files.py      # format sources
python automation/run_tests.py         # unit tests
python automation/run_asan.py          # tests under AddressSanitizer
python automation/run_tidy.py          # static analysis
git diff                               # review your own changes
```

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
