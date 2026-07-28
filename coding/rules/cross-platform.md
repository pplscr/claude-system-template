# 🖥️ cross-platform.md — Крос-платформна розробка

## Вузли мережі

| Ім'я | OS | Архітектура | Призначення |
|------|-----|------------|-------------|
| **mac-mini** | macOS 15.5 (Darwin) | arm64 (M4) | Розробка, стратег |
| **vuzol** | Linux (Ubuntu) | amd64 | Оркестратор, Qdrant, деплой |
| **hp-pavilion** | Windows 11 | amd64 | Windows-задачі |

## Визначення платформи в коді

```python
import platform, os, sys

system = platform.system()  # "Darwin" | "Linux" | "Windows"
machine = platform.machine()  # "arm64" | "x86_64" | "AMD64"

IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform == "win32"
IS_ARM = machine in ("arm64", "aarch64")
```

```javascript
const os = require('os');
const IS_MACOS = os.platform() === 'darwin';
const IS_LINUX = os.platform() === 'linux';
const IS_WINDOWS = os.platform() === 'win32';
const IS_ARM = os.arch() === 'arm64';
```

```bash
case "$(uname -s)" in
  Darwin)  OS="macos";  ARCH="$(uname -m)";;
  Linux)   OS="linux";  ARCH="$(uname -m)";;
  MINGW*|MSYS*|CYGWIN*) OS="windows"; ARCH="amd64";;
esac
```

## Еквіваленти команд

| Дія | macOS | Linux | Windows |
|-----|-------|-------|---------|
| Менеджер пакетів | `brew` | `apt` / `dnf` | `winget` / `choco` |
| Shell | `zsh` (default) | `bash` | PowerShell / Git Bash |
| Python | `python3` | `python3` | `python` |
| Pip | `pip3` | `pip3` | `pip` |
| Node/npm | `node` / `npm` | `node` / `npm` | `node` / `npm` |
| Home dir | `/Users/$USER` | `/home/$USER` | `C:\Users\$USER` |
| Temp dir | `$TMPDIR` | `/tmp` | `%TEMP%` |
| Config dir | `~/Library/...` | `~/.config/...` | `%APPDATA%\...` |
| PATH separator | `:` | `:` | `;` |
| Line ending | `\n` (LF) | `\n` (LF) | `\r\n` (CRLF) |
| Executable ext | (none) | (none) | `.exe` / `.bat` / `.ps1` |
| Symlink | `ln -s` | `ln -s` | `mklink` (Admin) |
| Permissions | `chmod` | `chmod` | `icacls` |
| Process list | `ps aux` | `ps aux` | `tasklist` |
| Kill process | `kill` | `kill` | `taskkill` |
| Env vars | `export X=Y` | `export X=Y` | `set X=Y` (cmd) / `$env:X="Y"` (PS) |

## Python: крос-платформний код

```python
import os
import sys
from pathlib import Path

# ✅ Правильно — pathlib
config_dir = Path.home() / ".config" / "myapp"
data_dir = Path(os.getenv("MYAPP_DATA", config_dir / "data"))

# ❌ Неправильно — хардкод macOS
config_dir = os.path.expanduser("~/Library/Application Support/myapp")

# ✅ Правильно — тимчасова директорія
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    ...

# ❌ Неправильно
tmp = "/tmp/myapp"  # не працює на Windows

# ✅ Правильно — запуск зовнішніх команд
import subprocess
result = subprocess.run(["git", "status"], capture_output=True, text=True)

# ❌ Неправильно
os.system("git status")  # проблеми з escaping на різних OS
```

## Shell: крос-платформний код

```bash
#!/usr/bin/env bash
# ✅ posix сумісний shebang

set -euo pipefail

# ✅ Використовуй env для пошуку команд
PYTHON="$(command -v python3 || command -v python)"

# ✅ Лапки навколо змінних
echo "Home: ${HOME}"

# ✅ [[ ]] замість [ ] (bash-only, але краще)
if [[ "$OS" == "macos" ]]; then
  PKG_MGR="brew"
elif [[ "$OS" == "linux" ]]; then
  PKG_MGR="apt"
fi

# ❌ Уникай platform-specific команд без перевірки
# brew install ...     # macOS only
# apt install ...      # Linux only
# winget install ...   # Windows only
```

## Git: крос-платформні налаштування

```bash
# LF в репозиторії, native в робочій копії
git config --global core.autocrlf input   # macOS/Linux
git config --global core.autocrlf true    # Windows

# Або через .gitattributes (рекомендовано)
echo "* text=auto" >> .gitattributes
echo "*.sh text eol=lf" >> .gitattributes
echo "*.bat text eol=crlf" >> .gitattributes
```

## Docker: крос-платформна збірка

```bash
# Створення multi-arch builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Збірка для всіх платформ
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myapp:latest \
  --push .
```

## Перевірка сумісності

```bash
# 1. Перевірка shell-скриптів
shellcheck scripts/*.sh

# 2. Пошук platform-specific шляхів
grep -r "/Users/\|/home/\|C:\\\\Users" --include="*.py" --include="*.js" .

# 3. Пошук platform-specific команд
grep -r "brew \|apt \|winget \|choco " --include="*.sh" .

# 4. Перевірка line endings
file scripts/*.sh | grep CRLF && echo "⚠️ Windows line endings in shell scripts!"
```
