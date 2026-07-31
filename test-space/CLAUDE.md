# Test Space — mac-mini

Тестовий простір для перевірки авто-відкриття.

## Що де лежить
| Файл | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |

## Qdrant Memory

- **Collection:** `space_test-space`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space test-space`
- **Sync:** files → `~/spaces/test-space/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/test-space/memory/agents/<name>/MEMORY.md`
