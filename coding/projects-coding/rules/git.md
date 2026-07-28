# 🌿 git.md — Git Workflow

## Стратегія гілок
```
main          — production-ready код
├── develop   — інтеграційна гілка
│   ├── feature/назва-фічі
│   ├── fix/назва-багу
│   └── refactor/що-рефакторимо
└── hotfix/   — термінові виправлення (від main)
```

## Повідомлення комітів (Conventional Commits)
Формат: `<type>: <short description>`

| Type | Призначення |
|------|-------------|
| `feat` | Нова функціональність |
| `fix` | Виправлення багу |
| `docs` | Зміни в документації |
| `style` | Форматування (пробіли, коми тощо) |
| `refactor` | Рефакторинг без зміни поведінки |
| `test` | Додавання/виправлення тестів |
| `chore` | Допоміжні зміни (залежності, CI) |
| `perf` | Покращення продуктивності |

### Приклади
```
feat: add user authentication via JWT
fix: resolve null pointer in order calculation
docs: update API documentation for v2
refactor: extract payment logic to separate module
chore: update ruff to 0.5.0
```

## Процес роботи
```bash
# 1. Початок фічі
git checkout develop
git pull origin develop
git checkout -b feature/нова-фіча

# 2. Коміти під час роботи
git add -p                    # інтерактивний stage
git commit -m "feat: ..."     # осмислене повідомлення

# 3. Перед push
git pull --rebase origin develop  # підтягнути зміни
# → пройти рев'ю (agents/reviewer.md)
# → запустити тести (agents/tester.md)

# 4. Push і Pull Request
git push origin feature/нова-фіча
# → створити PR у develop

# 5. Після мерджу
git checkout develop
git pull origin develop
git branch -d feature/нова-фіча
```

## Що НЕ комітити
- `.env` (файл із секретами)
- `node_modules/`, `__pycache__/`, `*.pyc`
- `.DS_Store`
- `venv/`, `.venv/`
- Файли IDE (`.idea/`, `.vscode/` — хіба що командні налаштування)
- Великі бінарні файли (зображення, моделі)
- Тимчасові файли (`*.tmp`, `*.log`)

## .gitignore (базовий)
```gitignore
# Secrets
.env
*.key
*.pem

# Python
__pycache__/
*.pyc
venv/
.venv/
dist/

# Node
node_modules/
dist/

# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/

# Logs
*.log
```
