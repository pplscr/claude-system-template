# 🧠 MEMORY.md — Пам'ять простору projects-coding

## Останнє оновлення
2026-07-28 — Multi-agent воркфлоу протестовано. Модель: стратег → agent.md (роль) → виконання.

## Активні проекти

| Проєкт | Статус | Опис |
|--------|--------|------|
| sysinfo | 🟢 done | Крос-платформний system info reporter |
| notify | 🟢 done | Cross-platform desktop notifications (macOS/Linux/Windows) |

## Завершені задачі

| Задача | Дата | Агенти | Результат |
|--------|------|--------|-----------|
| test-workflow-notify | 2026-07-28 | architect → dev → tester → reviewer | ✅ 18/18 tests, APPROVED, встановлено в ~/bin/ |
| test-workflow-sysinfo | 2026-07-28 | dev → tester → reviewer | ✅ 15/15 tests, APPROVED |
| task-test-e2e-01 | 2026-07-27 | dev | ✅ E2E пройдено |

## Модель воркфлоу (mac-mini)

```
СТРАТЕГ (я) → визначаю простір + агента
  │
  ├─ Читаю agents/<agent>.md — роль, обов'язки, процес
  ├─ Читаю rules/<rule>.md — стандарти (coding, security, cross-platform)
  ├─ ПРАЦЮЮ В РОЛІ АГЕНТА (не claude -p — role switch ефективніше)
  └─ Результат → tester → reviewer → done/
```

## Моделі агентів

| Агент | Модель | Коли |
|-------|--------|------|
| architect | deepseek-v4-pro] + thinking | Нова фіча, складна архітектура |
| dev | deepseek-v4-pro] | Код, рефакторинг |
| ops | deepseek-v4-pro] | Docker, CI/CD, деплой |
| tester | deepseek-v4-flash | Тести, баги |
| reviewer | deepseek-v4-flash | Рев'ю перед комітом |

## Конфігурація простору

| Параметр | Значення |
|----------|---------|
| Агентів | 5 (architect, dev, reviewer, tester, ops) |
| Правил | 4 (coding, git, security, cross-platform) |
| Платформ | 3 (macOS, Linux, Windows) |
| Інструментів | 2 (sysinfo, notify) |
