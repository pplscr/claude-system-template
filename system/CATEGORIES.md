# Task Categories — mac-mini

> Система категорій задач. Особисті / Робочі / Системні.

## Категорії

### 👤 Особисті (personal/)
Задачі пов'язані з особистим життям, фінансами, документами.

**Приклади:**
- Банківські кейси (CIBC)
- Фінансовий трекінг
- Особисті документи

### 💼 Робочі (work/)
Юридичні кейси, робочі проекти, бізнес-задачі.

**Приклади:**
- NSC Legal Case (factory-nsc)
- Enterprise Poland Dispute
- FW Debt
- Pantheon Office

### ⚙️ Системні (system/)
Технічна інфраструктура, сервери, мережа.

**Приклади:**
- Мережа A2A (vuzol + mac-mini + hp-pavilion)
- Claude Code налаштування
- Qdrant пам'ять
- Tailscale VPN

## Формат задачі

```markdown
---
task_id: <category>-<NNN>
priority: critical|high|normal|low
status: pending|in_progress|completed|blocked
category: personal|work|system
created: YYYY-MM-DD
deadline: YYYY-MM-DD (або null)
assigned: worker|explorer|code-review
source: vuzol|mac-mini|manual
---

# Назва задачі

## Опис
...

## Критерії готовності
- [ ] ...
```

## Правила

1. Кожна задача — окремий .md файл
2. completed → перемістити в done/
3. blocked → вказати blocked_reason
4. Після змін → `case-sync.sh push`
5. Особисті задачі не змішуються з робочими
