---
task_id: coding-02
priority: high
status: completed
category: coding
created: 2026-07-27
assigned: dev
---

# JSON Config Validator

## Опис
Створити CLI-утиліту для валідації JSON-конфігураційних файлів.
Інструмент має перевіряти:
1. Чи файл є валідним JSON
2. Чи присутні обов'язкові ключі
3. Чи значення відповідають типам (string, int, bool, list)
4. Виводити людський звіт про помилки

## Вимоги
- Python 3.9+ (type hints — обов'язково)
- argparse для CLI
- Кольоровий вивід (green/red/yellow)
- Підтримка schema-файлу (JSON Schema subset)
- Вихідний код: `workspace/json-validator/src/`
- Тести: `workspace/json-validator/tests/`

## Критерії готовності
- [ ] `validate.py` працює з --help
- [ ] Валідує структуру JSON
- [ ] Кольоровий вивід
- [ ] Тести pytest
- [ ] Пройдено рев'ю
- [ ] Задача → done/

## Приклад використання
```bash
python3 validate.py config.json --schema schema.json
# ✅ config.json: valid
# ⚠️  missing required key: 'port'
# ❌ 'timeout': expected int, got str
```

## Completion Log
- **Completed at**: 2026-07-27T21:22 UTC
- **Agent**: dev (Claude on mac-mini)
- **Duration**: ~8 min
- **Result**: ✅ PASSED

## Deliverables
- `workspace/json-validator/src/validate.py` — 230 lines, full type hints
- `workspace/json-validator/tests/test_validate.py` — 8 tests, all passing
- CLI: argparse, colored output, schema validation

## Test Results
```
8 passed, 0 failed
✅ valid JSON (no schema)
✅ invalid JSON syntax
✅ missing required key
✅ type mismatch (str vs int)
✅ all valid with schema
✅ file not found
✅ nested objects
✅ array items validation
```

## Code Quality
- ✅ Type hints (all functions)
- ✅ Google-style docstrings
- ✅ pathlib
- ✅ __future__ annotations
- ✅ argparse with --help
- ✅ Colored terminal output
- ✅ pytest-compatible tests
- ✅ DRY, KISS, SOLID
