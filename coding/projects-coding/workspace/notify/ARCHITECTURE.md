# Архітектура: notify — крос-платформні сповіщення

## Компоненти

```
notify.py (один файл, тільки stdlib)
├── _PROVIDER: Literal["osascript", "notify-send", "powershell", "print"]
├── _detect_provider() → визначає провайдер при імпорті
├── notify(title, message, urgency?) → основна функція
├── info(msg), warn(msg), error(msg) → скорочення з emoji
└── __main__: argparse CLI
```

## API функцій

| Функція | Параметри | Повертає |
|---------|-----------|----------|
| `notify(title, message, urgency="normal")` | title: str, message: str, urgency: low|normal|critical | None |
| `info(msg)` | msg: str | None |
| `warn(msg)` | msg: str | None |
| `error(msg)` | msg: str | None |

## Детектор платформи (при імпорті)

```python
import platform, sys

_PROVIDER = None  # кешується

def _detect_provider():
    system = platform.system()
    if system == "Darwin":
        return "osascript"
    elif system == "Linux":
        return "notify-send" if shutil.which("notify-send") else "print"
    elif system == "Windows":
        return "powershell"
    return "print"  # fallback
```

## Крос-платформні виклики

| Платформа | Команда |
|-----------|---------|
| macOS | `osascript -e 'display notification "msg" with title "title"'` |
| Linux | `notify-send "title" "msg" -u normal` |
| Windows | `powershell -Command "..."` (Toast) |
| Fallback | `print(f"[{level}] {title}: {msg}")` |

## Обробка помилок

- subprocess.CalledProcessError → logging.warning + fallback на print
- FileNotFoundError (немає інструменту) → fallback на print
- Невідома платформа → print (не крашитись)

## План реалізації

1. [x] `_detect_provider()` — визначення платформи
2. [x] `notify(title, message, urgency)` — основна функція
3. [x] `info/warn/error` — скорочення
4. [x] argparse CLI
5. [x] pytest тести
