---
name: legal-space-overview
description: "Legal Space — юридичні справи: Widerspruch, OLRB, OHSA, DFR, борги, прецеденти. 3 агенти: legal-analyst, email-drafter, doc-reviewer. 2 активні справи."
metadata:
  type: project
  node_type: memory
  space: legal
---

# Legal Space Overview

## Active Cases
1. **F&W Fordern & Wohnen** — €13,166 борг, 3. Mahnung
2. **Factory NSC** — Maneliuk v National Steel Car (DFR 3203-25-U)

## Agents (3)
- **legal-analyst** (T2, deepseek-v4-pro) — аналіз справ, законів, прецедентів
- **email-drafter** (T1, deepseek-v4-flash) — складання німецьких ділових листів
- **doc-reviewer** (T2, deepseek-v4-pro) — перевірка документів

## Key Deadlines
- 2026-08-05: Affidavit
- 2026-08-15: 3. Mahnung F&W
- 2026-08-17: Widerspruch

## Key Rules
- Всі листи німецькою у стилі німецького ділового листа
- Спочатку аналіз (legal-analyst) → потім дія (email-drafter)
- Завжди перевіряти Dokumentenabgabe (doc-reviewer)

## Structure
- `factory-nsc/` — справа NSC
- `fw-debt/` — справа F&W
- `case-db/` — база справ

## Resources
- Qdrant: space_legal
- Cost limit: $5/mo
