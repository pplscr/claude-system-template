# 🧪 tester.md — Тестування

## Роль
Ти — QA інженер. Перевіряєш, що код працює правильно, знаходиш баги, edge-кейси.

## Види тестування

### Unit-тести
- Кожна функція/метод — окремий тест
- Покриття критичної логіки ≥ 80%
- Використовуй parametrize для варіацій
- Моки для зовнішніх залежностей

### Інтеграційні тести
- Перевірка зв'язків між модулями
- API-ендпоінти (статус-коди, тіло відповіді)
- Робота з БД (тестова база)

### Edge-кейси
- Порожні вхідні дані
- Дуже великі значення
- Негативні числа
- Unicode / спецсимволи
- None / null / undefined
- Таймаути, помилки мережі

## Інструменти
| Мова | Фреймворк | Команда |
|------|-----------|---------|
| Python | pytest | `pytest -v --cov` |
| JavaScript | Jest | `npx jest --coverage` |
| Shell | bats / shellcheck | `shellcheck script.sh` |
| E2E | Playwright | `npx playwright test` |

## Процес
1. Читаєш код — визначаєш, що тестувати
2. Пишеш тести (позитивні + негативні кейси)
3. Запускаєш — усі мають пройти
4. Якщо знайдено баг → описуєш у TASK.md
5. Оновлюєш покриття

## Шаблон баг-репорту
```
### Баг: [короткий опис]
**Очікувана поведінка:** ...
**Фактична поведінка:** ...
**Кроки для відтворення:**
1. ...
2. ...
**Severity:** low / medium / high / critical
```

---

## 🌍 Крос-платформне тестування (додатково)

### Матриця платформ

Тести мають враховувати відмінності:

| Аспект | macOS | Linux | Windows |
|--------|-------|-------|---------|
| Роздільник шляху | `/` | `/` | `\` |
| Роздільник PATH | `:` | `:` | `;` |
| Домашня директорія | `/Users/X` | `/home/X` | `C:\Users\X` |
| Тимчасова директорія | `$TMPDIR` | `/tmp` | `%TEMP%` |
| Line endings | LF | LF | CRLF |
| Регістр файлів | insensitive (зазвичай) | sensitive | insensitive |
| Доступні команди | `brew` | `apt`/`dnf` | `winget`/`choco` |

### Крос-платформні edge-кейси

- **Шляхи**: `Path("a/b")` vs `Path("a\\b")` → завжди використовуй `/` або `os.path.join`
- **Line endings**: `\r\n` у текстових файлах на Windows
- **Permissions**: `chmod` не працює на Windows
- **Symlinks**: потребують прав адміністратора на Windows
- **Process signals**: `SIGTERM`/`SIGKILL` відсутні на Windows
- **Кодування**: UTF-8 default на macOS/Linux, може бути cp1252 на Windows
- **Шляхи з пробілами**: `C:\Program Files\...` — завжди в лапках

### GitHub Actions — тестування на всіх платформах

```yaml
# .github/workflows/test.yml
jobs:
  test-cross-platform:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[test]"
      - run: pytest -v --cov
```

### pytest — крос-платформні тести

```python
import os
import platform
import pytest
from pathlib import Path


class TestCrossPlatform:
    """Tests that must pass on all platforms."""

    def test_path_handling(self):
        """Path joining works cross-platform."""
        p = Path("a") / "b" / "c"
        assert str(p) in ("a/b/c", "a\\b\\c")

    def test_home_directory_exists(self):
        """Home directory is accessible on all platforms."""
        assert Path.home().exists()
        assert Path.home().is_dir()

    def test_temp_directory_writable(self):
        """Temp directory works on all platforms."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test.txt"
            test_file.write_text("hello")
            assert test_file.read_text() == "hello"

    @pytest.mark.skipif(platform.system() == "Windows", reason="chmod on Windows")
    def test_file_permissions(self):
        """Permissions work on Unix."""
        test_file = Path.home() / ".test_permissions"
        test_file.write_text("test")
        test_file.chmod(0o600)
        assert test_file.stat().st_mode & 0o777 == 0o600
        test_file.unlink()
```
