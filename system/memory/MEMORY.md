---
name: mac-mini-system-state
description: Current state of mac-mini node — hardware, software, agents, skills, services
metadata:
  type: project
  created: 2026-07-27
  updated: 2026-07-27
  node: mac-mini
---

# mac-mini — System State (2026-07-27)

## Hardware
- **Model**: Apple M4 (Mac16,10)
- **RAM**: 16GB
- **SSD**: 228GB (10GB used, 185GB free — 6%)
- **OS**: macOS 15.5 (24F74), Darwin 24.5.0
- **Hostname**: Ruslan's Mac mini

## Network
- **Tailscale**: 100.127.88.114 (mesh VPN)
- **Peers**: vuzol (100.84.177.33, direct relay), hp-pavilion (100.78.19.35, offline)
- **SSH**: vuzol reverse tunnel (launchd: com.vuzol.tunnel)

## Installed Software
| Tool | Version | Notes |
|------|---------|-------|
| Xcode CLT | latest | For Homebrew |
| Homebrew | - | /opt/homebrew |
| git | 2.39.5 | Apple bundled |
| Node.js | v22.14.0 | Prebuilt binary |
| npm | 11.17.0 | Bundled with Node |
| Python3 | - | macOS bundled |
| Claude Code | 2.1.220 | /opt/homebrew/bin/claude |
| Tailscale | latest | Mesh VPN |

## Claude Code Configuration
- **Provider**: DeepSeek v4-pro (1M context)
- **Model**: deepseek-v4-pro[1m]
- **Auth**: API key in settings.json env block
- **Permission mode**: acceptEdits (auto-approve edits, prompt for dangerous ops)
- **Auto compact**: enabled
- **Auto memory**: enabled

## Agents (5)
| Agent | File | Status |
|-------|------|--------|
| worker | ~/.claude/agents/worker.md | active |
| explorer | ~/.claude/agents/explorer.md | active |
| code-review | ~/.claude/agents/code-review.md | active |
| model-router | ~/.claude/agents/model-router.md | active |
| dispatcher | ~/.claude/agents/LOADING.md | active |

## Skills (5)
| Skill | File | Status |
|-------|------|--------|
| system-check | ~/.claude/skills/system-check.md | active |
| prompts | ~/.claude/skills/prompts.md | active |
| memory-sync | ~/.claude/skills/memory-sync.md | active |
| bootstrap | ~/.claude/skills/bootstrap.md | active |
| heartbeat | ~/.claude/skills/heartbeat.md | active |

## Spaces (4)
| Space | Path | Status |
|-------|------|--------|
| system | ~/spaces/system/ | active |
| orchestrator | ~/spaces/orchestrator/ | active |
| _template | ~/spaces/_template/ | active |
| projects-coding | ~/spaces/projects-coding/ | active |

## Scripts (4)
| Script | Path | Purpose |
|--------|------|---------|
| case-sync.sh | ~/.claude/scripts/case-sync.sh | Sync cases across nodes |
| compile-prompt.py | ~/.claude/scripts/compile-prompt.py | Compile prompts from templates |
| dispatch-mac.sh | ~/.claude/scripts/dispatch-mac.sh | Dispatch tasks to mac-mini |
| memory-bridge.sh | ~/.claude/scripts/memory-bridge.sh | Bridge memory to Qdrant |

## LaunchAgents (3)
| Agent | File | Purpose |
|-------|------|---------|
| browser-mcp | com.browser-mcp.plist | Browser MCP server |
| case-sync | com.mac-mini.case-sync.plist | Auto case sync |
| vuzol-tunnel | com.vuzol.tunnel.plist | SSH reverse tunnel to vuzol |

## Services
| Service | Type | Status |
|---------|------|--------|
| Tailscale | mesh VPN | running |
| com.vuzol.tunnel | SSH reverse tunnel (launchd) | needs reload after reboot |

## Pending
- [ ] macOS Tahoe update (538MB/9.8GB downloaded)
- [ ] HP Pavilion return from Justcom repair (~Aug 7)
- [ ] Create orchestrator space CLAUDE.md
- [ ] Set up _template space
- [ ] System reboot after macOS update
