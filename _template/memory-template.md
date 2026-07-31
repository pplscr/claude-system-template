---
name: memory-template
description: "Шаблон memory-секції для агентів — пошук перед роботою, збереження після"
tags: [memory, template, agents, workflow]
metadata:
  type: reference
  node_type: memory
---

# 🧠 Memory Workflow (стандарт для всіх агентів)

## 4 типи пам'яті

| Тип | Qdrant колекція | Що зберігати | Хто зберігає |
|-----|-----------------|-------------|-------------|
| **Системна** | `system_memory` | Архітектура, патерни, інфраструктура | mac-mini (стратег) |
| **Користувацька** | `user_memory` | Преференції, фідбек, правила | mac-mini (юзер) |
| **Просторова** | `space_<name>` | Рішення простору, контекст, knowledge | Всі агенти простору |
| **Агентська** | `agent_<space>_<name>` | Особистий досвід агента, помилки, прийоми | Кожен агент особисто |

## Перед роботою (ОБОВ'ЯЗКОВО)

```bash
# 1. Пошукати релевантний контекст у пам'яті простору
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "ключові слова" --space SPACENAME

# 2. Пошукати свій агентський досвід
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "ключові слова" --agent SPACENAME/AGENTNAME

# 3. Пошукати системні знання
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "ключові слова" --type system
```

## Після роботи (ОБОВ'ЯЗКОВО)

### Що зберігати в просторову пам'ять:
- ✅ Важливі рішення та їх обґрунтування
- ✅ Знайдені патерни та антипатерни
- ✅ Результати аналізу (коротко, з висновками)
- ✅ Контекст для наступної сесії

### Що зберігати в агентську пам'ять:
- ✅ Помилки, з якими зіткнувся, та як вирішив
- ✅ Ефективні прийоми та підходи
- ✅ Неефективні підходи (щоб не повторювати)
- ✅ Метрики: скільки часу/токенів/спроб зайняла задача

### Як зберегти:
```bash
# 1. Створити файл
# Для простору: ~/spaces/SPACENAME/memory/<name>.md
# Для агента:   ~/spaces/SPACENAME/memory/agents/AGENTNAME/<name>.md

# 2. Frontmatter:
# ---
# name: short-kebab-name
# description: "Одне речення — що це"
# tags: [tag1, tag2, tag3]
# type: space  # або agent
# agent: AGENTNAME  # тільки для agent-типу
# ---

# 3. Запуш в git → post-receive hook → авто-синхронізація з Qdrant
cd ~/.claude/projects/-Users-ruslanmaneliuk/memory
git add -A && git commit -m "memory: опис змін" && git push vuzol main

# Якщо авто-синхронізація не спрацювала — ручний reconcile:
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --reconcile
```

## Коли зберігати (тригери)

| Тригер | Що зберігати | Куди |
|--------|-------------|------|
| Завершив задачу | Ключові висновки, рішення | space |
| Знайшов новий патерн | Опис патерну, приклад | system |
| Зіткнувся з помилкою | Помилка + рішення | agent |
| Початок нової сесії | Контекст минулої сесії | agent |
| Важливе рішення | Обґрунтування | space |
| Зміна правил/преференцій | Нове правило | user |

## Перевірка

```bash
# Статистика всіх колекцій
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --stats

# Пошук по всій пам'яті
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "запит"

# Ручна пересинхронізація (якщо auto-hook не спрацював)
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --reconcile
```

> **Авто-синхронізація**: `git push vuzol main` → post-receive hook на vuzol → Qdrant.  
> Якщо push успішний але пошук не знаходить нове — `--reconcile`.
