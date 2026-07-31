# trading — Trading 212 Research & Analysis Skill

**Trigger:** trading, трейдинг, портфель, позиції, дивіденди, ринок, купити, продати, t212, інвестиції

## Purpose
Дослідження ринку, аналіз портфеля, генерація ідей. НЕ виконує трейди.

## Workflow

### 1. Sync
```bash
python3 ~/spaces/finance/trading212/sync.py --quick
```

### 2. Analyze
- Поточний стан портфеля (PPL, concentration, sectors)
- Останні транзакції/дивіденди

### 3. Research (якщо потрібно)
- Запустити `trading-research` агента (T2, deepseek-v4-pro)
- Сканувати ринок по заданих критеріях

### 4. Recommend
- Тільки інформаційно, з confidence level
- Завжди з risk assessment
- Ніколи без exit plan

## Rules
- Read-only за замовчуванням
- Будь-яка дія > €50 потребує підтвердження
- Stop-loss обов'язковий для всіх рекомендацій
- Макс 2% ризику на позицію (~€155)
