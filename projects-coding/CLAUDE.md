# 🤖 CLAUDE.md — Головні інструкції

## Мова
- **Відповідай українською.**
- Код, змінні, коментарі в коді — англійською.
- Повідомлення комітів — англійською.
- Документація, README, інструкції — українською.
- **Завжди показуй прогрес** виконання (що зроблено, що далі).

## Технічний стек (за замовчуванням)
| Категорія | Інструменти |
|-----------|-------------|
| **Мови** | Python 3.12+, JavaScript/TypeScript, Shell (bash) |
| **Бекенд** | FastAPI, Flask, Node.js |
| **Фронтенд** | React, Next.js, Tailwind CSS |
| **Бази даних** | PostgreSQL, SQLite, Redis |
| **DevOps** | Docker, docker-compose, GitHub Actions |
| **Тестування** | pytest (Python), Jest (JS), shellcheck (Bash) |
| **Лінтери** | ruff (Python), eslint (JS), prettier |

## Правила роботи
1. **Перед початком** — прочитай `SPACE.md`, щоб зрозуміти контекст простору.
2. **Кожна задача** — окрема тека в `tasks/active/`.
3. **Перед комітом** — пройди через агента `agents/reviewer.md`.
4. **Після змін** — оновлюй `memory/MEMORY.md`.
5. **Безпека** — дотримуйся `rules/security.md`.

## Швидкий старт
```bash
# Нова задача
mkdir -p tasks/active/назва-задачі
echo "## Опис\n\n## Прогрес\n- [ ] Початок" > tasks/active/назва-задачі/TASK.md

# Після завершення
mv tasks/active/назва-задачі tasks/done/
```
