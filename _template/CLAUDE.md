# Bootstrap: новий простір

> Це шаблон для створення нового простору. Скопіюй цю директорію і заповни.

## Крок 1: Копіювання

```bash
cp -r ~/spaces/_template ~/spaces/<назва>
```

## Крок 2: Ідентичність

Відредагуй `SPACE.md`:
- Назва простору
- Призначення (що робить, за що відповідає)
- На якому вузлі працює
- Статус

## Крок 3: Агенти

Створи агентів у `agents/` — мінімум один:
```markdown
# Agent: <назва>

## Role
...

## Instructions
...
```

## Крок 4: Пам'ять

Створи `memory/MEMORY.md` — початковий стан простору:
```markdown
# <space-name> — State

- **Node**: <вузол>
- **Created**: <дата>
- **Status**: active
```

## Крок 5: Зареєструй в orchestrator

Додай простір у `~/spaces/orchestrator/CLAUDE.md` → таблиця Available Spaces.

## Крок 6: Зареєструй в system

Додай простір у `~/spaces/system/memory/MEMORY.md` → таблиця Spaces.

## Перевірка

- [ ] `SPACE.md` заповнено
- [ ] Мінімум 1 агент у `agents/`
- [ ] `memory/MEMORY.md` створено
- [ ] `workspace/` готовий до роботи
- [ ] Простір зареєстровано в orchestrator
- [ ] Простір зареєстровано в system memory
