#!/bin/bash
TIMEOUT=5
OK=0; FAIL=0

echo "=== $(date -u) ==="

check() { if eval "$2"; then echo "✅ $1"; ((OK++)); else echo "❌ $1"; ((FAIL++)); fi; }

check "Tailscale" "tailscale status &>/dev/null"
check "SSH mac-mini" "ssh -o ConnectTimeout=$TIMEOUT -o BatchMode=yes mac-mini hostname &>/dev/null"
check "Qdrant" "curl -sf --connect-timeout $TIMEOUT http://localhost:6333/healthz | grep -q passed"
check "Docker" "docker ps &>/dev/null"
check "nginx" "curl -sf -o /dev/null --connect-timeout $TIMEOUT http://localhost:80/"
check "ttyd" "curl -sf -o /dev/null --connect-timeout $TIMEOUT http://localhost:7681/"

echo "---"
echo "Результат: $OK ✅ / $FAIL ❌"
