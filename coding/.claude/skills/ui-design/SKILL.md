---
name: ui-design
description: UI/UX дизайн — метод, правила, довідники. Активувати коли: «дизайн», «UI», «стиль», «кольори», «шрифти», «spacing», «layout», «анімація», «accessibility», «зроби гарно», «оформи», «вигляд», «інтерфейс», «component», «кнопка», «форма», «dashboard», «landing».
---

# UI Design Method

Застосовуй цей метод до будь-якої UI-задачі.

## Метод (4 кроки)

```
1. PLAN    — Токени (4-6 кольорів, 1-2 шрифти, spacing scale) + layout + signature element
2. BUILD   — Токени → компоненти → сторінки. Структурний скелет перед кольорами.
3. AUDIT   — AI-slop check, контраст (4.5:1), focus, reduced-motion, heading hierarchy
4. POLISH  — States (hover/active/focus/disabled/loading/empty/error), мікро-деталі
```

## Швидкі правила (не порушуй)

- **8px grid**: тільки 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 96, 128px
- **oklch()** для кольорів — жодного hex/rgb. Один `--brand-hue` → вся палітра
- **44×44pt** touch target мінімум
- **Disabled = 40% opacity** (не 50%)
- **Hover = ≥8% lightness delta**
- **WCAG AA**: 4.5:1 текст, 3:1 великий
- **Шрифти**: 1-2 families max, 5 sizes max. НЕ Inter/Roboto/Open Sans.
- **НІКОЛИ**: purple gradients, emoji іконки, 3 однакові картки, Sarah M.
- **`prefers-reduced-motion`** завжди, `:focus-visible` завжди

## Anti-AI-Slop (fail = перероби)

Шрифт не Inter | немає purple gradient | немає emoji іконок | немає 3 однакових карток | кольори oklch()

## References (завантажуй за потребою)

- `references/color.md` — oklch(), brand-hue, dark mode, contrast grid
- `references/typography.md` — type scale, font pairing, tracking, fluid clamp()
- `references/layout.md` — grid, container queries, safe areas, spacing cheat sheet
- `references/animation.md` — spring physics, timing, reduced-motion, gestures
- `references/accessibility.md` — WCAG AA checklist, ARIA, forms, testing
