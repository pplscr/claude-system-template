# 📐 coding.md — Правила кодингу

## Загальні принципи
- **DRY** — Don't Repeat Yourself. Кожен фрагмент знань має бути в одному місці.
- **KISS** — Keep It Simple, Stupid. Прості рішення — найкращі.
- **SOLID** — 5 принципів ООП для підтримуваного коду.
- **YAGNI** — You Ain't Gonna Need It. Не пиши те, що не потрібно зараз.

## Python
```python
# ✅ Правильно
def calculate_total(items: list[dict], tax_rate: float = 0.2) -> float:
    """Calculate order total including tax."""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    return round(subtotal * (1 + tax_rate), 2)

# ❌ Неправильно
def calc(itms, tr=.2):
    s=0
    for i in itms: s+=i['price']*i['qty']
    return s*(1+tr)
```

### Вимоги
- Type hints — обов'язкові
- Docstrings для публічних функцій/класів (Google style)
- `ruff` для лінтінгу, `ruff format` для форматування
- f-рядки замість `.format()` або `%`
- `pathlib` замість `os.path`
- `dataclass` / `pydantic` для структур даних
- Обробка помилок через конкретні exceptions (не `except Exception`)

## JavaScript / TypeScript
```javascript
// ✅ Правильно
const calculateTotal = (items, taxRate = 0.2) => {
  const subtotal = items.reduce((sum, { price, quantity }) => sum + price * quantity, 0);
  return +(subtotal * (1 + taxRate)).toFixed(2);
};

// ❌ Неправильно
function calc(i,t){var s=0;for(var x=0;x<i.length;x++)s+=i[x].p*i[x].q;return s*(1+(t||.2))}
```

### Вимоги
- `const`/`let` — ніякого `var`
- Arrow functions для колбеків
- Destructuring для об'єктів/масивів
- Optional chaining `?.`
- Template literals
- `eslint` + `prettier`
- TypeScript бажаний

## Shell / Bash
```bash
# ✅ Правильно
#!/usr/bin/env bash
set -euo pipefail

readonly CONFIG_DIR="${HOME}/.config/myapp"
for file in "$CONFIG_DIR"/*.conf; do
  [[ -f "$file" ]] || continue
  echo "Processing: ${file}"
done

# ❌ Неправильно
for f in ~/.config/myapp/*.conf; do echo Processing: $f; done
```

### Вимоги
- `#!/usr/bin/env bash` — shebang
- `set -euo pipefail` — суворий режим
- Лапки навколо змінних (`"$var"`)
- `[[ ]]` замість `[ ]` для умов
- `readonly` / `declare -r` для констант
- `shellcheck` обов'язковий

## Структура проекту
```
project/
├── src/            # вихідний код
├── tests/          # тести (дзеркалять src/)
├── docs/           # документація
├── scripts/        # допоміжні скрипти
├── .env.example    # приклад змінних оточення
├── .gitignore
├── pyproject.toml  # або package.json, Cargo.toml
└── README.md
```
