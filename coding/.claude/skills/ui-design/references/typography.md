# Typography Reference

> Завантажується при виборі шрифтів, побудові type scale, налаштуванні ієрархії.

## Type Scale (Apple HIG + Refactoring UI)

```
11px — caption, legal, overline
13px — small body, metadata, timestamps
15px — compact body (dashboards, data-dense UI)
17px — body (Apple HIG baseline)
20px — large body, small headline
24px — title, card heading
28px — section title
36px — headline
48px — display
56px+ — hero display
```

**Hard rules:**
- Максимум 5 розмірів на одну сторінку
- Кожен розмір має чітку роль (не «десь 15, десь 16, десь 17»)
- Line-height: display/headline = 1.05–1.2, body = 1.5, caption = 1.4

## Letter-Spacing (Tracking)

```
56px+ (hero)     : -0.03em   — оптична корекція для великих розмірів
36-48px (display): -0.02em
24-28px (title)  : -0.01em
17-20px (body)   : 0         — не чіпай
13-15px (small)  : +0.01em
11px (caption)   : +0.03em   — розрідження для читабельності малого
```

## Font Pairing

### Apple Native
```
Display/Headings: SF Pro Display
Body: SF Pro Text
Mono: SF Mono
```
Використовуй на iOS/macOS. Автоматично через `Font.body`, `Font.title` тощо.

### Web — Перевірені (не заїжджені)
```
# Варіант 1: Source Sans 3 + Source Serif 4
Headings: Source Sans 3 (weight: 600-700)
Body: Source Sans 3 (weight: 400)
Accent: Source Serif 4 (для pull-quotes, testimonials)

# Варіант 2: IBM Plex Sans + IBM Plex Mono
Headings: IBM Plex Sans (weight: 500-600)
Body: IBM Plex Sans (weight: 400)
Code: IBM Plex Mono

# Варіант 3: Instrument Sans + Newsreader
Headings: Newsreader (serif, weight: 500)
Body: Instrument Sans (weight: 400)
```

### НІКОЛИ (без явного запиту)
- Inter — найбанальніший AI-шрифт
- Roboto — Android default, виглядає як default
- Open Sans — «я не вибрав шрифт»
- Lato — «Open Sans був недоступний»

## Font Weight Hierarchy

```
Regular (400)  — body text
Medium (500)   — emphasis, labels, captions
Semibold (600) — subtitles, card headings, navigation
Bold (700)     — main headings, buttons
```

**Hard rules:**
- Не використовуй light (300) для body тексту — низький контраст
- Не використовуй bold (700) для body тексту — важко читати
- Display/hero текст можна light (300) — декоративний, не функціональний

## Line-Height (Leading)

```css
--leading-display: 1.05;   /* 56px+ */
--leading-headline: 1.2;   /* 24-48px */
--leading-title: 1.3;      /* 20-24px */
--leading-body: 1.5;       /* 15-17px */
--leading-caption: 1.4;    /* 11-13px */
```

## Line Length (Measure)

```
45-75 символів — оптимальна ширина рядка для читання
~65 символів — ідеал для body тексту
Не >75 символів — очі втомлюються повертатися
```

```css
.reading-width {
  max-width: 65ch; /* ch = ширина символу '0' */
}
```

## Fluid Typography (clamp)

```css
/* Замість breakpoints — fluid масштабування */
--text-body: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
--text-title: clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem);

/* Формула: clamp(MIN, PREFERRED, MAX) */
/* PREFERRED = MIN(rem) + (MAX - MIN) * (100vw / MAX_VIEWPORT) */
```

## CSS Font Stack

```css
:root {
  --font-sans: 'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-serif: 'Source Serif 4', 'Iowan Old Style', 'Apple Garamond', serif;
  --font-mono: 'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace;

  font-family: var(--font-sans);
}
```

## Поширені Помилки

- ❌ 8+ розмірів шрифту на сторінці
- ❌ body текст <15px
- ❌ line-height: 1 для body
- ❌ Всі заголовки одного розміру
- ❌ Inter/Roboto без потреби
- ✅ 4–5 розмірів, чітка ієрархія
- ✅ Body 17px, line-height 1.5
- ✅ Display негативний tracking
