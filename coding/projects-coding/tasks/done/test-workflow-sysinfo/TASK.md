# Задача: sysinfo — кросплатформний system info reporter
**Створено**: 2026-07-28
**Завершено**: 2026-07-28
**Пріоритет**: medium (тестовий)
**Простір**: projects-coding

## Опис
Написати Python-скрипт `sysinfo.py`, який виводить інформацію про систему.

## Агенти
| Крок | Агент | Статус |
|------|-------|--------|
| 1. Написати код | dev | ✅ |
| 2. Протестувати | tester | ✅ |
| 3. Відрев'юїти | reviewer | ✅ APPROVED |

## Прогрес
- [x] Крок 1: dev — sysinfo.py (116 рядків, type hints, docstrings, pathlib)
- [x] Крок 2: tester — 15 тестів passed, macOS ✅, Linux ✅
- [x] Крок 3: reviewer — безпека ✅, якість ✅, крос-платформа ✅

## Результат
- `workspace/sysinfo/sysinfo.py` — основний скрипт
- `workspace/sysinfo/tests/test_sysinfo.py` — 15 тестів
- Працює на macOS (arm64) + Linux (x86_64)
