# ~/spaces/ — Filesystem-as-State Hierarchy

> **Files are truth. DB is cache.** One pipeline: edit file → parse → sync → PostgreSQL.
> Every fact that must survive across sessions lives in a file. Git = audit trail.

## The Hierarchy

```
~/                                        ← mac-mini home
├── CLAUDE.md                             ← symlink → claude-system/config/CLAUDE.md
├── AGENTS.md                             ← symlink → claude-system/config/AGENTS.md
├── claude-system/                        ← ВСІ скрипти, конфіги, агенти, бекапи
│   ├── config/                           ← CLAUDE.md, AGENTS.md (симлінки сюди)
│   ├── scripts/                          ← ~20 скриптів (tasks-parse, sync-to-vuzol, ...)
│   ├── archive/                          ← старі звіти, файли
│   └── backups/                          ← бекапи
├── .claude/                              ← Claude Code config
│   ├── settings.json                     ← hooks, env, modelRouting (єдиний, без .bak!)
│   ├── hooks/                            ← 9 хуків (session-init, precompact, ...)
│   ├── skills/                           ← 8 skills (consilium, dispatch, ...)
│   ├── rules/                            ← 4 правила (git, model-routing, ...)
│   ├── projects/                         ← state.py кеш (→ _infra/projects/ канонічне)
│   └── memory/                           ← файлова пам'ять (→ Qdrant)
└── spaces/                               ← робочі простори
    ├── README.md                         ← цей файл
    ├── tasks-all.json                    ← АГРЕГАЦІЯ (генерується)
    ├── _template/                        ← blueprint простору
    │   ├── SPACE.md, CLAUDE.md, task.json, .mcp.json
    │   ├── agents/, rules/, skills/, memory/
    ├── _infra/                           ← серверна інфраструктура
    │   ├── projects/                     ← 9 канонічних проектних JSON
    │   └── config/, scripts/, docker/, nginx/, systemd/
    └── <space>/                          ← доменний простір
        ├── SPACE.md, CLAUDE.md, task.json
        ├── agents/, rules/, skills/, memory/
        ├── items/*.json                  ← bills/tickets (finance)
        └── <case>/                       ← справа (legal)
            ├── CASE.md                   ← наратив
            └── case.json                 ← правда (status, deadlines, progress)
```

## The Pipeline

```
Edit case.json    →    tasks-parse.py    →    tasks-all.json
   (truth)              (aggregate)            (generated)

Edit project.json →    sync-to-vuzol.sh  →    scp vuzol   →   state3.py migrate  →  PostgreSQL
   (_infra/projects/)   (every 5m auto)        (JSON push)     (JSON→DB upsert)      (TG bot reads)
```

## Who Owns Each Fact

| Fact | Writable source | Consumers |
|------|----------------|-----------|
| Case status, progress, deadlines | `<space>/<case>/case.json` | task.json, tasks-all.json, state3.py PG |
| Project status, progress | `_infra/projects/<id>.json` | tasks-all.json, state3.py PG |
| Bill / subscription | `finance/items/<id>.json` | tasks-all.json |
| Narrative context | `CASE.md` | humans, agents |

## Rules

1. **Edit the leaf, not the aggregate** — change `case.json`, then run `tasks-parse.py`
2. **Never hand-edit `tasks-all.json`** — it's regenerated
3. **Completed ≠ urgent** — deadlines with `status: completed` are excluded
4. **Files first, DB second** — PostgreSQL mirrors files, never leads
5. **Sync is automatic** — launchd `task-sync` (5 min) + `sync-to-vuzol.sh`

## Creating a New Space

```bash
cp -r _template <name>
# edit SPACE.md, CLAUDE.md, task.json
python3 ~/claude-system/scripts/tasks-parse.py
```

## Syncing to vuzol

```bash
# Manual:
bash ~/claude-system/scripts/sync-to-vuzol.sh

# Automatic: launchd every 5 min (task-sync) + heartbeat (sync-to-vuzol)
```

## Global vs Per-Space

| Ресурс | Глобальний (всі простори) | Per-space (тільки свій) |
|--------|--------------------------|------------------------|
| CLAUDE.md | `~/CLAUDE.md` (root, завжди) | `<space>/CLAUDE.md` (при cwd) |
| Агенти | — | `<space>/agents/` |
| Правила | `~/.claude/rules/` | `<space>/rules/` |
| Skills | `~/.claude/skills/` (8) | `<space>/skills/` (рідко) |
| Хуки | `~/.claude/hooks/` (9) | — |
| Скрипти | `~/claude-system/scripts/` | — |
| Пам'ять | `~/.claude/projects/*/memory/` | `<space>/memory/` |

**Динамічне відкриття:** `ls` у кожній категорії → Claude сам бачить що з'явилось. Жодного хардкоду.

## vuzol (100.84.177.33)

```
/root/
├── .claude/           ← credentials.env (єдиний), settings.json, hooks
├── scripts/           ← state3.py, task-api.py, qdrant-check.sh, ...
├── cases/             ← cibc, fw-debt, enterprise-poland
├── factory-nsc/       ← активна справа (mac ↔ vuzol rsync)
├── мережа/            ← docker-compose (qdrant, litellm, beszel, ...)
└── archive/           ← старі файли
```
