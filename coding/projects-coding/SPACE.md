# 🏠 SPACE.md — Ідентичність простору

## Назва
**projects-coding** — простір розробки на mac-mini.

## Домен
Розробка програмного забезпечення, код, технічні проекти, DevOps.

## Машини

| Ім'я | OS | Роль |
|------|-----|------|
| **mac-mini** | macOS 15.5 (M4, 16GB) | Основний вузол розробки |
| vuzol | Linux (x86_64, 16GB) | Оркестратор, Qdrant |
| hp-pavilion | Windows 11 (x86_64, 16GB) | Windows-сумісні задачі |

## Пам'ять — Qdrant (vuzol:6333)
Контекст, історія, знання — у Qdrant. Локально — лише код і tasks/.
```bash
~/.claude/scripts/memory-bridge.sh search "..." system_memory
```

## Крос-платформна підтримка
Код пишеться для **macOS + Linux + Windows**. Правила — `rules/cross-platform.md`.

## Агенти простору

| Агент | Файл | Роль |
|-------|------|------|
| `architect` | `agents/architect.md` | Проєктує архітектуру, API, схеми БД |
| `dev` | `agents/dev.md` | Пише код |
| `reviewer` | `agents/reviewer.md` | Рев'юїть перед комітом |
| `tester` | `agents/tester.md` | Тестує, шукає баги |
| `ops` | `agents/ops.md` | DevOps: Docker, CI/CD, деплой |

## Правила простору

| Правило | Файл |
|---------|------|
| Стандарти коду | `rules/coding.md` |
| Git workflow | `rules/git.md` |
| Безпека | `rules/security.md` |
| Крос-платформна розробка | `rules/cross-platform.md` |

## Роль Клода щодо цього простору
Клод-стратег (mac-mini) отримує задачу → визначає, що це домен «кодинг» → делегує агентам цього простору. Сам Клод-стратег код не пише — це роблять агенти.

## Порядок роботи

```
Задача
  │
  ├─ 1. architect — спроєктувати (якщо нова фіча)
  ├─ 2. dev — написати код
  ├─ 3. tester — протестувати
  ├─ 4. reviewer — відрев'юїти
  └─ 5. ops — задеплоїти (якщо потрібно)
```

## Власник
- @ruslanmaneliuk

## Правила простору
1. Один проект — одна тека в `workspace/`
2. Кожна задача має TASK.md
3. Перед push — обов'язкове рев'ю через агента `reviewer`
4. Жодних секретів у репозиторії (`rules/security.md`)
5. Код має працювати на macOS + Linux + Windows (`rules/cross-platform.md`)
6. Агенти виконують, Клод-стратег — координує
