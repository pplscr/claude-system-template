# 🔒 security.md — Безпека

## Головне правило
**Жодних секретів у коді чи репозиторії. Ніколи.**

## Що вважається секретом
- 🔑 API-ключі (OpenAI, Stripe, AWS, etc.)
- 🔐 Паролі, токени доступу
- 📧 Email-паролі, SMTP-креденшели
- 🗄️ Рядки підключення до БД (з паролями)
- 🔒 Приватні ключі (`.pem`, `.key`)
- 🍪 Секретні ключі (JWT secret, session secret, Flask secret key)
- 🪙 Крипто-гаманці, seed-фрази

## Як працювати з секретами

### Локально
```bash
# .env (НЕ КОМІТИТИ)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost/db

# .env.example (КОМІТИТИ — без реальних значень)
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:password@localhost/db
```

### У коді
```python
# ✅ Правильно — читати з env
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")

# ❌ Неправильно — захардкоджено
api_key = "sk-abc123def456"  # НІКОЛИ!
```

### Docker
```dockerfile
# ✅ Використовуй secrets / env_file
# ❌ НЕ копіюй .env у образ
```

## Перевірка перед комітом
```bash
# 1. Пошук потенційних секретів
grep -r "sk-\|api_key\|password\|secret\|token" --include="*.py" --include="*.js" | grep -v ".env.example"

# 2. Перевірка, що .env у .gitignore
grep "^\.env$" .gitignore || echo "⚠️  .env не в .gitignore!"

# 3. git-secrets (рекомендовано)
brew install git-secrets
git secrets --scan
```

## Якщо секрет потрапив у репозиторій
1. **Негайно** відклич/зміни ключ на стороні сервісу
2. Видали з історії:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch шлях/до/файлу" \
     --prune-empty -- --all
   ```
3. Повідом команду

## Валідація даних
```python
# ✅ Завжди валідуй вхідні дані
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    age: int = Field(ge=0, le=150)

# ✅ Параметризовані запити
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ НІКОЛИ не конкатенуй SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection!
```

## Залежності
- Регулярно оновлюй: `pip list --outdated`, `npm outdated`
- Перевіряй уразливості: `pip-audit`, `npm audit`
- Не використовуй застарілі/непідтримувані пакети
