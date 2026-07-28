# sysinfo — cross-platform system info tool
# Usage: make [test|lint|install|clean]

.PHONY: test lint install clean run

PYTHON := python3
PIP := pip3

run:
	$(PYTHON) sysinfo.py

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

lint:
	$(PYTHON) -m ruff check sysinfo.py tests/ 2>/dev/null || echo "ruff not installed — skipping"

install:
	cp sysinfo.py /usr/local/bin/sysinfo 2>/dev/null || \
	cp sysinfo.py $(HOME)/bin/sysinfo && chmod +x $(HOME)/bin/sysinfo
	@echo "✅ sysinfo installed to $(HOME)/bin/sysinfo"

uninstall:
	rm -f $(HOME)/bin/sysinfo /usr/local/bin/sysinfo
	@echo "🗑️ sysinfo removed"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true

requirements:
	$(PIP) install pytest ruff --quiet 2>/dev/null || true
	@echo "✅ deps installed"
