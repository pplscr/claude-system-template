# 🧠 Система пам'яті — трирівнева архітектура

```
Рівень 1: SHORT-TERM           Рівень 2: SEMANTIC          Рівень 3: DURABLE
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ Qdrant checkpoints   │    │ Qdrant collections   │    │ PostgreSQL           │
│ (173 точки)          │    │                      │    │ orchestrator (8.2MB) │
│                      │    │ system_memory (93)   │    │                      │
│ + сесійні файли      │    │ rozum (104)          │    │ + файли пам'яті      │
│                      │    │ user_memory (28)     │    │   mac-mini           │
│                      │    │                      │    │                      │
│ Точний ID пошук      │    │ Cosine семантика     │    │ SQL + ACID           │
│ Швидкий (ms)         │    │ Ембедінг-пошук (ms)  │    │ Повільний (SQL, >ms) │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Як працює

```
mac-mini                    vuzol
   │                           │
   │  пам'ять (файл .md)       │
   ├──────────────────────────►│  ~/.claude/projects/-root/memory/{system,user}/
   │                           │
   │                           ├── memory-to-qdrant.py ──► Qdrant (вектори)
   │                           ├── memory-to-rozum.py ──► Qdrant rozum (вектори)
   │                           │
   │  пошук "щось"             │
   ├──────────────────────────►│  Qdrant Cosine → top-5
   │                           │  fallback: PostgreSQL текстовий
   │                           │
   │  ←──────────── result ────┤
```

## Команди

```bash
# Пошук
python3 /root/scripts/memory-to-qdrant.py --search "запит"              # всі колекції
python3 /root/scripts/memory-to-qdrant.py --search "запит" --type system # system_memory
python3 /root/scripts/memory-to-qdrant.py --search "запит" --type user   # user_memory
python3 /root/scripts/memory-to-qdrant.py --search "запит" --space NAME  # простір

# Синхронізація
python3 /root/scripts/memory-to-qdrant.py              # файли → Qdrant
python3 /root/scripts/memory-to-qdrant.py --type system # лише system
python3 /root/scripts/memory-to-qdrant.py --text       # без ембедінгів (fallback)
```

## Структура файлів пам'яті

```
~/.claude/projects/-root/memory/
├── system/               ← знання про систему
│   ├── some-fact.md
│   └── ...
├── user/                 ← знання про користувача
│   ├── preference.md
│   └── ...
└── MEMORY.md             ← індекс всіх memory-файлів
```

## Правила

1. Спочатку PostgreSQL (ACID), потім Qdrant (семантичний індекс)
2. НЕ роби LLM-виклики в hot path пам'яті — ембедінг це векторна математика
3. Якщо embedding API не відповідає → fallback на текстовий пошук (`--text`)
4. fail-soft: Qdrant впав → PostgreSQL текстовий пошук → не краш
