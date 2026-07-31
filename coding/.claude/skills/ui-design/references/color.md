# Color System Reference

> Завантажується коли потрібно: палітра, вибір кольорів, dark mode, contrast.

## oklch() — Єдиний Формат

oklch(Lightness, Chroma, Hue) — перцептивно рівномірний простір.
На відміну від HSL, однакові зміни L дають однаково сприйману зміну яскравості.

```css
/* Формат */
--color-name: oklch(L C H);

/* L = Lightness (0-1, але в CSS: 0%-100%) */
/* C = Chroma (насиченість, 0-0.4 типова) */
/* H = Hue (0-360 градусів) */
```

## Brand-Hue Pattern

```css
--brand-hue: 250; /* ЄДИНЕ число, яке змінюється при ребрендингу */

/* Accent scale */
--color-accent: oklch(0.65 0.2 var(--brand-hue));
--color-accent-hover: oklch(0.72 0.18 var(--brand-hue));
--color-accent-active: oklch(0.58 0.22 var(--brand-hue));
--color-accent-muted: oklch(0.55 0.12 var(--brand-hue));
--color-accent-subtle: oklch(0.95 0.02 var(--brand-hue));
```

## Семантичні Токени (Light Mode)

```css
/* Text */
--color-text-primary: oklch(0.15 0.01 var(--brand-hue));
--color-text-secondary: oklch(0.45 0.01 var(--brand-hue));
--color-text-tertiary: oklch(0.60 0.01 var(--brand-hue));
--color-text-disabled: oklch(0.65 0.01 var(--brand-hue)); /* ~40% opacity */
--color-text-inverse: oklch(0.98 0 var(--brand-hue));

/* Surface */
--color-surface: oklch(0.98 0.002 var(--brand-hue));
--color-surface-elevated: oklch(1 0 var(--brand-hue));
--color-surface-sunken: oklch(0.94 0.002 var(--brand-hue));

/* Border */
--color-border: oklch(0.87 0.01 var(--brand-hue));
--color-border-hover: oklch(0.70 0.02 var(--brand-hue));
--color-border-focus: oklch(0.65 0.2 var(--brand-hue));
```

## Dark Mode (prefers-color-scheme: dark)

```css
/* Text */
--color-text-primary: oklch(0.92 0.01 var(--brand-hue));    /* НЕ білий! */
--color-text-secondary: oklch(0.72 0.01 var(--brand-hue));
--color-text-tertiary: oklch(0.55 0.01 var(--brand-hue));
--color-text-disabled: oklch(0.45 0.01 var(--brand-hue));

/* Surface */
--color-surface: oklch(0.14 0.005 var(--brand-hue));
--color-surface-elevated: oklch(0.20 0.005 var(--brand-hue));
--color-surface-sunken: oklch(0.10 0.005 var(--brand-hue));

/* Border */
--color-border: oklch(0.28 0.01 var(--brand-hue));
--color-border-hover: oklch(0.40 0.02 var(--brand-hue));
```

## Contrast Grid (Перевірка)

| Foreground | Background | Ratio | Pass AA? |
|-----------|------------|-------|----------|
| text-primary (0.15) | surface (0.98) | 14:1 | ✅ AAA |
| text-secondary (0.45) | surface (0.98) | 5.8:1 | ✅ AA |
| text-tertiary (0.60) | surface (0.98) | 3.2:1 | ⚠️ Large only |
| accent (0.65) | surface (0.98) | 2.8:1 | ❌ Text, ✅ Icons |
| accent (0.65) | surface-sunken (0.94) | 2.4:1 | ❌ |

**Правило:** Якщо accent на фоні — тільки для іконок/бордерів, не для тексту.
Для accent-тексту використовуй темніший варіант: `oklch(0.45 0.18 var(--brand-hue))`.

## Кількість Кольорів

- **4–6 кольорів** у палітрі, не більше
- 1 accent + 3 neutral (text) + 2 surface
- Не створюй окремий колір для кожної сторінки
- Семантичні токени — єдине джерело

## High Contrast Mode

```css
@media (prefers-contrast: more) {
  --color-text-primary: oklch(0.05 0 var(--brand-hue));
  --color-text-secondary: oklch(0.30 0 var(--brand-hue));
  --color-border: oklch(0.50 0 var(--brand-hue));
  --color-border-focus: oklch(0.30 0.2 var(--brand-hue));
}
```

## Поширені Помилки

- ❌ `color: #333; background: #fff;` — хардкод
- ❌ `color: hsl(0, 0%, 20%);` — не перцептивний
- ❌ 10+ кольорів у палітрі
- ❌ Різні accent для різних компонентів
- ❌ `#FFFFFF` для тексту в dark mode — halation
- ✅ Семантичні токени через oklch()
- ✅ Один accent + neutral scale
- ✅ Dark mode: текст = oklch(0.92 ...)
