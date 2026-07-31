# Animation & Motion Reference

> Завантажується при: анімаціях, переходах, мікро-взаємодіях, жестах.

## Spring Physics (Apple)

```css
/* Critically damped — для більшості UI */
.spring-settle {
  transition: transform 0.35s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* Momentum-driven — для жестів (flick, drag) */
.spring-bouncy {
  transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Весняний CSS (2026) */
@keyframes spring-in {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
```

## Timing by Type

| Тип | Duration | Easing |
|-----|----------|--------|
| Hover color/opacity | 150ms | ease-out |
| Toggle, checkbox | 150ms | ease-out |
| Tooltip in/out | 200ms | ease-out |
| Modal in | 200ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Modal out | 150ms | ease-in |
| Panel/sheet slide | 250ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Page transition | 300ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Drag release settle | 400ms | spring: damping=1.0, response=0.3 |
| Scroll-driven | залежить від scroll | linear |

## Velocity Handoff (Жести)

```
Жест → анімація без шва:

1. Жест закінчується з velocity V
2. Передай V як initial velocity анімації
3. Анімація починається з presentation value (не target!)
4. Користувач НЕ бачить стрибка

❌ Помилка: gesture ends → jump to target → animate
✅ Правильно: gesture ends → continue from current position → settle
```

## Momentum Projection

```javascript
// Apple exponential decay
const decelerationRate = 0.998;
const projection = velocity * decelerationRate / (1 - decelerationRate);

// Де зупиниться? → snap до найближчої цілі
const target = snapToNearest(projection, targets);
```

## Rubber-Banding

```javascript
// Прогресивний опір, не жорстка стіна
function rubberBand(offset, maxOffset) {
  if (Math.abs(offset) <= maxOffset) return offset;
  const excess = Math.abs(offset) - maxOffset;
  const resistance = 0.55; // що менше → більший опір
  return Math.sign(offset) * (maxOffset + excess * resistance);
}
```

## Reduced Motion

```css
/* Всі анімації мають поважати цей медіа-запит */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* АБО — заміни на opacity cross-fade */
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: opacity 0.2s ease-out;
  }
}
```

## Scroll-Driven Animations (CSS 2026)

```css
/* Анімація прив'язана до scroll position */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.scroll-reveal {
  animation: fade-in linear;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

## View Transitions API

```css
/* Плавний перехід між сторінками */
@view-transition {
  navigation: auto;
}

::view-transition-old(root) {
  animation: 0.3s ease-in both fade-out;
}

::view-transition-new(root) {
  animation: 0.3s ease-out both fade-in;
}
```

## Micro-Interactions

```
Button press:
  transform: scale(0.97) — 100ms ease-out
  → release: scale(1) — 200ms spring

Card hover:
  transform: translateY(-2px) — 200ms ease-out
  box-shadow: md → lg — 200ms ease-out

List item enter (staggered):
  opacity: 0 → 1 + translateY(8px → 0)
  delay: index * 50ms
  duration: 300ms per item

Loading skeleton:
  background: shimmer animation — infinite
  pulse: opacity 0.4 ↔ 0.7 — 1.5s ease-in-out infinite
```

## Timing Cheat Sheet

```
Instant         (0ms)    — color, opacity на hover
Micro           (150ms)  — toggle, checkbox, hover lift
Quick           (200ms)  — tooltip, small overlay
Standard        (300ms)  — modal, panel, page transition
Deliberate      (400ms)  — drag settle, hero animation
Slow reveal     (600ms)  — complex entrance, splash
```

## Поширені Помилки

- ❌ `transition: all 0.3s` — анімуй конкретні властивості
- ❌ Анімації без `prefers-reduced-motion`
- ❌ `animation-delay: 1s` — занадто довго, користувач пішов
- ❌ Блокування input під час анімації
- ❌ Лінійна інтерполяція (`linear`) для UI
- ✅ `transition: transform 0.2s, opacity 0.2s`
- ✅ `@media (prefers-reduced-motion: reduce)`
- ✅ Не блокуй scroll/click під час анімацій
