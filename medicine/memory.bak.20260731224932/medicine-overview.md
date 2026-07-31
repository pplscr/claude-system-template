---
name: medicine-space-overview
description: "Medicine Space — аналіз лабораторних результатів, симптомів, медичної літератури. 3 агенти: diagnostician, lab-analyst, researcher. НЕ ставить діагнозів."
metadata:
  type: project
  node_type: memory
  space: medicine
---

# Medicine Space Overview

## Purpose
Аналіз лабораторних результатів, симптомів, медичної літератури. **НЕ ставить діагнозів.**

## Agents (3)
- **diagnostician** (T2, deepseek-v4-pro) — симптоми → 3-5 можливих причин (НЕ остаточний діагноз)
- **lab-analyst** (T2, deepseek-v4-pro) — аналізи крові/сечі, референсні значення, відхилення
- **researcher** (T1, deepseek-v4-flash) — PubMed, гайдлайни, статті

## Key Rules
- Українською — всі відповіді користувачу
- Безпека — завжди: «це не медична консультація, звернись до лікаря»
- lab-analyst → тільки аналізи, не симптоми
- diagnostician → тільки гіпотези, не діагнози
- researcher → доказова медицина

## Structure
- `knowledge/` — медична література, гайдлайни
- `workspace/` — робочі файли

## Resources
- Max agents: 5
- Cost limit: $5/mo
- Qdrant: space_medicine
