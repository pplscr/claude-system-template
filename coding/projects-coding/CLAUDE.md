# 🤖 CLAUDE.md — Головні інструкції (projects-coding)

## Пам'ять — Qdrant (vuzol:6333)

Контекст зберігається в Qdrant, не в локальних файлах. Перед початком роботи — пошукай релевантний контекст:

```bash
~/.claude/scripts/memory-bridge.sh search "<тема>" system_memory
~/.claude/scripts/memory-bridge.sh search "<тема>" rozum
```

Після важливих рішень — збережи в Qdrant:

```bash
~/.claude/scripts/memory-bridge.sh store "<що варто запам'ятати>" system_memory
```

## Мова
- **Відповідай українською.**
- Код, змінні, коментарі в коді — англійською.
- Повідомлення комітів — англійською (Conventional Commits).
- Документація, README, інструкції — українською.
- **Завжди показуй прогрес** виконання.

## Платформи
Код пишеться для **macOS + Linux + Windows**.

| Вузол | OS | Де |
|-------|-----|-----|
| mac-mini | macOS (M4) | Розробка тут |
| vuzol | Linux (Ubuntu) | Деплой, Qdrant, оркестратор |
| hp-pavilion | Windows 11 | Windows-тестування |

## Агенти простору

| Агент | Коли викликати |
|-------|---------------|
| `architect` | Нова фіча, складна архітектура, API дизайн |
| `dev` | Написання/зміна коду |
| `tester` | Тестування, пошук багів |
| `reviewer` | Перед комітом — обов'язково |
| `ops` | Docker, CI/CD, деплой |

## Правила (читай за потреби)

| Правило | Файл |
|---------|------|
| Стандарти коду | `rules/coding.md` |
| Git workflow | `rules/git.md` |
| Безпека | `rules/security.md` |
| Крос-платформна розробка | `rules/cross-platform.md` |

## Швидкий старт

```bash
# Нова задача
mkdir -p tasks/active/назва-задачі
cat > tasks/active/назва-задачі/TASK.md << 'TASK'
# Задача: [назва]
**Створено**: $(date +%Y-%m-%d)
**Пріоритет**: medium

## Опис
...

## Прогрес
- [ ] Початок
TASK

# Після завершення
mv tasks/active/назва-задачі tasks/done/
~/.claude/scripts/memory-bridge.sh store "Завершено: назва-задачі — результат" system_memory
```

## Порядок роботи
```
1. Отримав задачу → dispatch (якщо код → цей простір)
2. Пошукав контекст у Qdrant → memory-bridge.sh search
3. Нова фіча? → architect (спроєктувати)
4. Написати код → dev
5. Протестувати → tester
6. Відрев'юїти → reviewer (ОБОВ'ЯЗКОВО)
7. Задеплоїти? → ops
8. Оновити memory/MEMORY.md (локально)
9. Зберегти ключове в Qdrant → memory-bridge.sh store
10. git commit + push
```

## Крос-платформні нагадування
- Використовуй `pathlib` (Python) / `path.join` (JS) — не хардкод `/Users/...`
- Перевіряй платформу перед platform-specific командами
- Тестуй на GitHub Actions з matrix: `[ubuntu, macos, windows]`
- `.gitattributes`: `* text=auto`
