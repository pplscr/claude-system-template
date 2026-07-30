# 🖥️ Beszel — UI Reference & Agent Guide

> **Hub:** http://100.84.177.33:8090  
> **User:** `monitor@vuzol.local`  
> **Version:** 0.18.7  
> **Agents:** mac-mini (LaunchAgent) + vuzol (Docker)

---

## 🎨 UI Overview

Beszel — lightweight, dark-themed, SvelteKit SPA. No bloat. Clean data density.

```
┌──────────────────────────────────────────────────────┐
│  🔍 Search systems...          ☀️/🌙  ⚙️ Settings    │  ← Top bar
├──────────┬───────────────────────┬───────────────────┤
│          │                       │                   │
│  SYSTEM  │   📊 METRICS          │   📋 DETAILS      │
│  LIST    │                       │                   │
│          │   ┌─────────────────┐ │   CPU Model        │
│  ● mac-  │   │ CPU ████░░ 13%  │ │   Threads          │
│    mini  │   │ RAM ████░░ 56%  │ │   OS Version       │
│          │   │ DISK ████░░ 32% │ │   Uptime           │
│  ● vuzol │   │ NET ██████████  │ │                    │
│          │   └─────────────────┘ │   🐳 Containers    │
│  + Add   │                       │   ├─ vaultwarden   │
│  System  │   📈 HISTORY (1h-7d) │   ├─ beszel-agent   │
│          │   ┌─────────────────┐ │   ├─ qdrant        │
│          │   │ ╱╲  ╱╲         │ │   ├─ dozzle        │
│          │   │ ╱  ╲╱  ╲  ╱╲   │ │   ├─ uptime-kuma   │
│          │   │╱        ╲╱  ╲  │ │   └─ beszel        │
│          │   └─────────────────┘ │                   │
└──────────┴───────────────────────┴───────────────────┘
```

### Grid layout
- **Left panel** (280px): System list with status dots (🟢 up / 🔴 down / 🟡 warning)
- **Center** (flex): Real-time charts — CPU, RAM, Disk, Network. Time range: 15m → 7d
- **Right/details** (320px): System info, container list, systemd services, SMART devices

### Color system
| Color | Hex | Meaning |
|-------|-----|---------|
| Green | `#22c55e` | Healthy, online |
| Yellow | `#d29922` | Warning (high load) |
| Red | `#ef4444` | Critical, offline |
| Blue | `#79c0ff` | Accent, links |
| Grey | `#8b949e` | Secondary text |

### Key interactions
1. **Click system** → metrics/detail panels update
2. **Time range tabs** → 15m, 1h, 4h, 12h, 1d, 7d
3. **⚙️ Settings** → Add System, Tokens, Users, Alerts, OAuth
4. **+ Add System** → generates agent KEY/TOKEN pair for new nodes

---

## 🤖 Agent API

### Health check (quick)

```bash
# All systems status
curl -s http://100.84.177.33:8090/api/collections/systems/records \
  -H "Authorization: Bearer <user_token>" | jq '.items[] | {name, status, updated}'
```

### Metric thresholds (alert on these)

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU | > 80% | > 95% |
| RAM | > 75% | > 90% |
| Disk | > 80% | > 90% |
| System down | — | immediate |

### Data freshness

| Collection | Update interval | Retention |
|------------|----------------|-----------|
| `system_stats` (1m) | 60s | 7 days |
| `system_stats` (10m) | 600s | 30 days |
| `system_stats` (1h) | 3600s | 1 year |
| `containers` | 60s | last state |
| `system_details` | on change | last state |

---

## 📡 Architecture

```
┌───────────────────────┐
│    Beszel Hub :8090    │  PocketBase (SQLite) + SvelteKit
│    /api/beszel/        │
│    ├─ agent-connect    │  WebSocket upgrade (agents push metrics)
│    ├─ getkey           │  Hub SSH public key
│    └─ universal-token  │  Auto-registration token mgmt
└───────┬───┬───────────┘
        │   │
   ┌────┘   └────┐
   ▼             ▼
┌──────┐    ┌──────────┐
│vuzol │    │ mac-mini  │
│agent │    │  agent    │
│Docker│    │LaunchAgent│
└──────┘    └──────────┘
```

### Auth flow
```
Agent starts → reads KEY + TOKEN
             → WS connect to HUB_URL/api/beszel/agent-connect
             → Hub validates TOKEN (universal_tokens collection)
             → Creates system record if new
             → Agent pushes metrics every 10s (1m stats) + 10m + 1h
```

### Universal token
- **Type:** Permanent (survives hub restart)
- **Scope:** Any agent with this token auto-registers
- **Rotate:** via Settings → Tokens & Fingerprints in UI
- **Current:** `bb683bf9-6668-46d4-9f9a-7bc19297b620`

---

## 🧠 Agent Instructions

When checking system health, follow this sequence:

```
1. API check     →  curl systems/records  →  is status "up"?
2. Stats check   →  curl system_stats      →  are metrics flowing?
3. Agent check   →  ps aux | grep (mac) / docker logs (vuzol)
4. Direct check  →  ssh free/df/docker ps  →  only if 1-3 fail
```

### Example: full health check

```bash
TOKEN=$(curl -s -X POST http://100.84.177.33:8090/api/collections/users/auth-with-password \
  -H 'Content-Type: application/json' \
  -d '{"identity":"monitor@vuzol.local","password":"BeszelMonitor2026!"}' | jq -r '.token')

curl -s "http://100.84.177.33:8090/api/collections/systems/records" \
  -H "Authorization: Bearer $TOKEN" | jq -c '.items[] | {name, status, updated}'
```

---

## ⚡ Quick Reference

```bash
# Get token
curl -s -X POST .../api/collections/users/auth-with-password

# Systems
GET  /api/collections/systems/records          # all systems
GET  /api/collections/system_stats/records     # metrics (perPage, sort, filter)
GET  /api/collections/containers/records       # docker containers
GET  /api/collections/system_details/records   # cpu, ram, disk, os info
GET  /api/beszel/getkey                        # hub public key
GET  /api/beszel/universal-token               # token status
GET  /api/beszel/universal-token?enable=1&permanent=1  # create token

# Dashboard
http://100.84.177.33:8090                      # full UI
http://100.84.177.33:8090/api/                 # PocketBase REST
```

---

## 🔐 Security

| Layer | Detail |
|-------|--------|
| Transport | HTTP (internal Tailscale mesh, not exposed to internet) |
| Auth | JWT via PocketBase `users` collection |
| Agent Auth | Universal token (UUID v4) + Hub SSH key |
| UI Access | Behind Tailscale IP, Cloudflare tunnel for external |
| Credentials | Not committed to git, stored in `beszel-setup.md` (local only) |

---

*UI Style 2030 — Clean. Dark. Data-first. No distractions.*
