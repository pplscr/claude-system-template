# mac-mini — Стратег + Виконавець

macOS 15 | M4 | 16GB | Claude Code + DeepSeek V4 Pro

## Роль

Приймати рішення, запускати агентів, керувати workflow, звітувати.

## Структура

```
~/
├── CLAUDE.md              ← головні інструкції (symlink → claude-system/config/)
├── AGENTS.md              ← subagent-mcp інваріант
├── .claude/
│   ├── settings.json      ← API ключі, модель, permissions
│   └── rules/             ← глобальні правила (git, model, security, resources)
├── claude-system/
│   ├── config/            ← оригінали CLAUDE.md, AGENTS.md
│   ├── scripts/           ← healthcheck, cleanup, heartbeat
│   └── backups/           ← історія конфігурацій
└── spaces/                ← ізольовані зони для агентів
    ├── _template/         ← шаблон нового простору
    ├── coding/            ← код, розробка
    ├── legal/             ← юридичні справи
    └── medicine/          ← медичні кейси
```

## Встановлення з нуля

```bash
# 1. Симлінки
ln -sf ~/claude-system/config/CLAUDE.md ~/CLAUDE.md
ln -sf ~/claude-system/config/AGENTS.md ~/AGENTS.md

# 2. Правила
cp rules/*.md ~/.claude/rules/

# 3. Простір
cp -r spaces/_template ~/spaces/новий-простір/
# → заповни SPACE.md і CLAUDE.md
```

## Простори

Кожен простір = ізольована зона. Агенти простору не бачать чужі дані.

Створити новий: `cp -r _template/ назва/` → заповнити `SPACE.md`.
