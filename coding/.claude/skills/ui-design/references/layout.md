# Layout & Spacing Reference

> Завантажується при: компонуванні сторінок, responsive дизайні, налаштуванні grid.

## 8px Grid System

```
 4px — fine gap (icon-to-text, inline spacing tweaks)
 8px — tight gap (related elements, compact padding)
12px — compact card padding (vertical), list item gap
16px — standard padding (horizontal), card content gap, list gap
20px — outer padding (mobile horizontal)
24px — section gap, generous card padding
32px — major section gap, outer padding (desktop)
40px — hero/content region padding
48px — section separator
64px — page-level vertical rhythm
96px — sparse section spacing
128px — maximum whitespace
```

## Grid Structure

```css
/* 12-column desktop */
.page-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  padding-inline: 32px;
}

/* 4-column mobile */
@media (max-width: 768px) {
  .page-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding-inline: 16px;
  }
}

/* Column spans */
.col-full  { grid-column: span 12; }   /* 12/12 — full width */
.col-half  { grid-column: span 6; }    /* 6/12 — 50% */
.col-third { grid-column: span 4; }    /* 4/12 — 33% */
.col-two-thirds { grid-column: span 8; } /* 8/12 — 66% */
.col-quarter { grid-column: span 3; }  /* 3/12 — 25% */
```

## Container Queries (Новий Стандарт)

```css
/* Компонент сам вирішує свій layout */
.card-grid {
  container-type: inline-size;
  container-name: card-grid;
}

@container card-grid (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

@container card-grid (min-width: 600px) {
  .card {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
```

## Breakpoints (Mobile-First)

```css
/* Mobile-first: починай з найменшого */
/* Базовий стан — mobile (320px+) */

/* Small: large phone / small tablet */
@media (min-width: 640px) { ... }

/* Medium: tablet portrait */
@media (min-width: 768px) { ... }

/* Large: tablet landscape / small desktop */
@media (min-width: 1024px) { ... }

/* XL: desktop */
@media (min-width: 1280px) { ... }

/* 2XL: large desktop */
@media (min-width: 1536px) { ... }

/* ❌ НІКОЛИ: @media (max-width: ...) — це desktop-first */
```

## Spacing Tokens (Tailwind v4 @theme)

```css
@theme {
  --spacing-1: 4px;     /* fine */
  --spacing-2: 8px;     /* tight */
  --spacing-3: 12px;    /* compact */
  --spacing-4: 16px;    /* base */
  --spacing-5: 20px;    /* mobile outer */
  --spacing-6: 24px;    /* section */
  --spacing-8: 32px;    /* desktop outer, major section */
  --spacing-10: 40px;   /* hero padding */
  --spacing-12: 48px;   /* separator */
  --spacing-16: 64px;   /* page rhythm */
  --spacing-24: 96px;   /* sparse */
  --spacing-32: 128px;  /* maximum */
}
```

## Safe Areas

```css
.page {
  /* iOS safe areas */
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Для fixed bottom nav */
.bottom-nav {
  padding-bottom: max(16px, env(safe-area-inset-bottom));
}
```

## Visual Hierarchy (Layout Signals)

```
Порядок уваги (зверху вниз, зліва направо):

1. РОЗМІР       — найбільший елемент = найважливіший
2. ПОЗИЦІЯ      — верх/зліва = першочергове
3. КОЛІР/ВАГА   — accent/bold = привертає увагу
4. ПРОСТІР      — більше простору навколо = важливіше
5. ТИП  — унікальний елемент виділяється на фоні повторюваних

⚠️ Не використовуй усі 5 одночасно — 2-3 достатньо.
```

## Content Width

```css
/* Optimal reading width */
.content {
  max-width: 65ch;    /* ~65 символів на рядок */
  margin-inline: auto;
}

/* Wide content (dashboards, tables) */
.content-wide {
  max-width: 1200px;
  margin-inline: auto;
}

/* Narrow content (forms, sign-in) */
.content-narrow {
  max-width: 480px;
  margin-inline: auto;
}
```

## Spacing Cheat Sheet

| Контекст | Mobile | Desktop |
|----------|--------|---------|
| Outer padding | 16px | 32px |
| Section gap | 24px | 32px |
| Card padding (v) | 12px | 16px |
| Card padding (h) | 16px | 16px |
| List item gap | 12px | 16px |
| Form field gap | 16px | 20px |
| Button gap | 12px | 16px |
| Icon-to-text | 8px | 8px |
| Label-to-input | 4px | 4px |

## Поширені Помилки

- ❌ `gap: 15px` — не з 8px шкали
- ❌ `padding: 13px 19px` — довільні значення
- ❌ `@media (max-width: 768px)` — desktop-first
- ❌ `max-width: 1000px` — використовуй 960px або 1024px (кратні 8)
- ❌ Фіксована ширина без max-width
- ✅ Значення з 8px шкали
- ✅ Mobile-first min-width
- ✅ Container queries для компонентів
