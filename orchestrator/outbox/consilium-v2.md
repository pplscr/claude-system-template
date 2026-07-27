Here's what I found about **vuzol** on your system:

## 🔍 Vuzol — Reverse SSH Tunnel Service

It's a **LaunchAgent** (`com.vuzol.tunnel`) that sets up a reverse SSH tunnel to a remote server:

| Detail | Value |
|---|---|
| **Config** | `/Users/ruslanmaneliuk/Library/LaunchAgents/com.vuzol.tunnel.plist` |
| **Remote host** | `root@100.84.177.33` |
| **Forward** | Remote `:2222` → local `:22` (SSH) |
| **Forward** | Remote `:5901` → local `:5900` (VNC) |
| **SSH Key** | `~/.ssh/id_ed25519` |

---

## ❌ Problem: The tunnel is **failing repeatedly**

The error log (`/tmp/vuzol-tunnel.err`) is flooded with:

```
Error: remote port forwarding failed for listen port 2222
```

This means **port 2222 is already in use** on the remote server (`100.84.177.33`), likely from a previous stale connection or another service.

---

What would you like me to do?

- **Fix the tunnel** — kill the stale process on the remote server to free port 2222, then restart
- **Disable it** — unload the LaunchAgent
- **Check connectivity** — verify the remote server is reachable
- Something else?
