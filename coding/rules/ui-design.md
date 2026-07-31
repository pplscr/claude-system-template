# 🎨 UI Design Rules — непохитні, з числами

> Не поради. Не «рекомендації». Це закони дизайну для всього, що генерується в цьому просторі.

## Spacing Scale (8px Grid)

```
4px   — fine adjustments (icon-to-text gap)
8px   — element gap, inline padding
12px  — compact card padding (vertical)
16px  — standard card padding (horizontal), section padding, list gap
20px  — outer padding (mobile horizontal)
24px  — section gap, card padding (generous)
32px  — major section gap, outer padding (desktop)
40px  — hero section padding
48px  — section separator
64px  — page-level vertical rhythm
96px  — full-viewport section spacing
128px — maximum whitespace
```

**Hard rule:** Жодних довільних значень. Тільки з цієї шкали. Жодних `7px`, `13px`, `19px`, `25px`, `33px`.

## Typography Scale

```
11px — minimum (captions, legal)
13px — small (captions, metadata)
15px — compact body (dashboards)
17px — body (Apple HIG baseline)
20px — large body, small headlines
24px — title, card headings
28px — section titles
36px — headline
48px — display
56px+ — hero display (-0.03em letter-spacing)
```

**Hard rules:**
- Максимум 5 розмірів на сторінку
- Мінімум 1.5 line-height для body
- 1.05–1.2 line-height для display/headline
- Letter-spacing: негативний для ≥36px, нуль для body, позитивний для ≤13px
- 1–2 font families максимум

## Color System Rules

### Один brand-hue → вся палітра (oklch)

```css
--brand-hue: 250;  /* єдине число, яке змінюється */

/* Derived via oklch() math — НЕ хардкодь hex */
--color-accent: oklch(0.65 0.2 var(--brand-hue));
--color-accent-hover: oklch(0.72 0.18 var(--brand-hue));
--color-accent-muted: oklch(0.55 0.12 var(--brand-hue));
```

### Семантичні токени (ніколи не сирі hex/rgb)

```css
--color-text-primary: oklch(0.15 0.01 var(--brand-hue));     /* dark mode: 0.92 */
--color-text-secondary: oklch(0.45 0.01 var(--brand-hue));   /* dark mode: 0.72 */
--color-text-disabled: oklch(0.65 0.01 var(--brand-hue));    /* 40% opacity ефект */
--color-surface: oklch(0.98 0.002 var(--brand-hue));         /* dark mode: 0.12 */
--color-surface-elevated: oklch(1 0 var(--brand-hue));       /* dark mode: 0.16 */
--color-border: oklch(0.87 0.01 var(--brand-hue));           /* dark mode: 0.25 */
```

### Hard rules
- Жодного `#fff`, `#000`, `#333`, `#666` — тільки семантичні токени
- Жодного HSL — тільки oklch (перцептивна рівномірність)
- 4–6 кольорів у палітрі, не більше
- Один accent для всіх інтерактивних елементів
- Dark mode: `--color-text-primary` = oklch(0.92 ...), не `#FFFFFF`

## Contrast (WCAG 2.2 AA)

| Елемент | Мінімум | Ідеал |
|---------|---------|-------|
| Body text (<18pt) | 4.5:1 | 7:1 |
| Large text (≥18pt / ≥14pt bold) | 3:1 | 4.5:1 |
| Icons, borders | 3:1 | 4.5:1 |
| Disabled text | Немає вимоги | 3:1 бажано |

## Touch & Interaction

- **44×44pt** — мінімальний touch target (Apple HIG)
- **48×48pt** — рекомендований для важливих дій
- Focus ring: `outline: 2px solid var(--color-accent); outline-offset: 2px`
- Disabled: `opacity: 0.4` (не 0.5!)
- Hover: lightness delta ≥8%
- Active/pressed: scale 0.97–0.98 або lightness delta ≥12%

## Animation Timing

| Тип | Duration | Easing |
|-----|----------|--------|
| Micro-interaction (hover, toggle) | 150–200ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| UI transition (modal, panel) | 200–300ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Page transition | 300–400ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Spring settle (drag release) | 400–600ms | spring: damping=1.0, response=0.3 |
| Opacity cross-fade (reduced-motion) | 200ms | `ease-out` |

## Elevation (Z-axis)

```css
--shadow-xs: 0 1px 2px rgba(0,0,0,0.04);        /* subtle lift */
--shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-md: 0 4px 6px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.04);
--shadow-xl: 0 20px 25px rgba(0,0,0,0.10), 0 8px 10px rgba(0,0,0,0.04);
```

## Breakpoints (Mobile-First)

```css
/* Базовий: mobile (320px+) */
/* 640px+  — large phone / small tablet */
/* 768px+  — tablet portrait */
/* 1024px+ — tablet landscape / small desktop */
/* 1280px+ — desktop */
/* 1536px+ — large desktop */
```

**Hard rule:** Пиши mobile-first. `min-width`, ніколи `max-width`. Використовуй container queries для компонентів.

## States (Обов'язковий набір)

Кожен інтерактивний компонент має мати:
1. **Default** — базовий стан
2. **Hover** — курсор над елементом
3. **Focus** — клавіатурний фокус (`:focus-visible`)
4. **Active** — натиснення
5. **Disabled** — неактивний (opacity: 0.4)
6. **Loading** — очікування (skeleton/spinner для конкретного компонента)
7. **Error** — помилка валідації
8. **Empty** — немає даних (`ContentUnavailableView`)

## Anti-Patterns (автоматичний fail)

Код, що містить будь-що з цього без явного запиту користувача, — **fail**:

- `font-family: Inter` (або Roboto/Open Sans/Lato)
- `background: linear-gradient(...)` з purple/blue/indigo
- `border-left: 3px solid` на картках
- Emoji в UI (⚠️ 🔒 🚀 ✨ 🎉)
- `box-shadow: 0 4px 6px -1px` на 3+ однакових картках у ряд
- `text-align: center` на body-тексті
- Фейкові імена (Sarah M., John D., Alex T.)
- `bg-gray-50` / `bg-slate-100` — generic світлі фони

## Responsive Design Rules

- Mobile-first: `min-width`, ніколи `max-width`
- Container queries для компонентів: `@container (min-width: 320px)`
- `clamp()` для fluid типографіки: `font-size: clamp(1rem, 0.8rem + 1vw, 1.25rem)`
- Зображення: `max-width: 100%; height: auto`
- Таблиці: `overflow-x: auto` на mobile, не ламай layout
- Тестуй 320px–2560px

## Icons

- **SF Symbols** (Apple) — 5000+ іконок, multiple weights, rendering modes
- **Lucide** / **Phosphor** (web) — consistent, crisp, 1.5px stroke
- Розміри: 16px (inline), 20px (UI), 24px (navigation), 28px+ (feature)
- Завжди `aria-hidden="true"` з окремим `aria-label` на батьківському елементі
- **Ніколи** emoji як іконки

## Крос-платформні Rules

| Платформа | Font | Icon System | Design Kit |
|-----------|------|-------------|------------|
| iOS/iPadOS | SF Pro | SF Symbols | Apple Design Resources |
| macOS | SF Pro | SF Symbols | Apple Design Resources |
| Web | Source Sans 3 / IBM Plex Sans | Lucide / Phosphor | Tailwind / CSS |
| Android | Roboto (виняток!) | Material Symbols | Material 3 |
| Flutter | Roboto / SF Pro | Material Symbols / Cupertino | Material 3 / Cupertino |
