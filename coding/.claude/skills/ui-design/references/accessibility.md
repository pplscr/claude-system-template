# Accessibility Reference

> Завантажується при: accessibility audit, a11y перевірках, формах, навігації.

## WCAG 2.2 AA Checklist (Мінімум)

### Контраст
- [ ] Body текст (<18pt): 4.5:1
- [ ] Великий текст (≥18pt / ≥14pt bold): 3:1
- [ ] Іконки, бордери: 3:1
- [ ] Focus ring: 3:1 проти фону
- [ ] Перевірено в Light + Dark режимах

### Клавіатура
- [ ] Всі інтерактивні елементи досяжні через Tab
- [ ] Focus order = візуальний порядок (логічний)
- [ ] Focus ring видимий на всіх елементах
- [ ] Немає клавіатурних пасток (keyboard traps)
- [ ] Escape закриває модалки/dropdown
- [ ] Enter/Space активує кнопки та посилання
- [ ] Arrow keys навігують у списках/табах/меню
- [ ] Skip-to-content лінк на початку сторінки

### Screen Reader
- [ ] Усі зображення мають `alt` (декоративні: `alt=""`)
- [ ] Іконки: `aria-hidden="true"` + `aria-label` на батьківському
- [ ] Форми: `<label>` пов'язаний з `<input>` (не тільки placeholder)
- [ ] Заголовки: h1 → h2 → h3 без пропусків
- [ ] Landmarks: `<nav>`, `<main>`, `<aside>`, `<footer>`
- [ ] Динамічний контент: `aria-live` для оновлень
- [ ] Error messages: `aria-describedby` зв'язаний з полем

### Touch & Pointer
- [ ] Touch target ≥ 44×44px (рекомендовано 48×48px)
- [ ] Відстань між touch targets ≥ 8px
- [ ] Жести не конфліктують з системними
- [ ] Альтернатива для складних жестів (tap або menu)

### Motion
- [ ] `prefers-reduced-motion` поважається
- [ ] Немає миготливого контенту (>3 flashes/sec)
- [ ] Анімації <5 секунд (або з pause/stop)

### Color & Сприйняття
- [ ] Інформація не передається ТІЛЬКИ кольором
- [ ] Помилки: іконка + текст + колір (не тільки червоний)
- [ ] Графіки: patterns + colors, не тільки кольори
- [ ] `prefers-contrast: more` підтримується

## Focus Management

```css
/* ❌ НІКОЛИ */
:focus { outline: none; }           /* вбиває a11y */
*:focus { outline: none; }          /* геноцид фокусу */

/* ✅ ПРАВИЛЬНО */
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Виняток: кастомний focus ring для кнопок */
button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-surface), 0 0 0 4px var(--color-accent);
}
```

## ARIA Cheat Sheet

```html
<!-- Розкривний блок -->
<button aria-expanded="false" aria-controls="menu-1">Меню</button>
<div id="menu-1" hidden>...</div>

<!-- Tab list -->
<div role="tablist" aria-label="Секції">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
</div>
<div role="tabpanel" id="panel-1">...</div>

<!-- Діалог -->
<dialog aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <h2 id="dialog-title">Заголовок</h2>
  <p id="dialog-desc">Опис дії</p>
</dialog>

<!-- Live region -->
<div aria-live="polite" aria-atomic="true">
  <!-- Динамічний контент -->
</div>

<!-- Alert (негайно) -->
<div role="alert">
  Помилка! Перевірте дані.
</div>
```

## Skip Link

```html
<!-- Перший елемент у <body> -->
<a href="#main-content" class="skip-link">
  Skip to content
</a>

<style>
.skip-link {
  position: absolute;
  top: -100%;
  left: 16px;
  z-index: 9999;
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
}
.skip-link:focus {
  top: 16px;
}
</style>
```

## Form Accessibility

```html
<!-- ✅ Правильно -->
<div class="field">
  <label for="email">Email адреса</label>
  <input
    type="email"
    id="email"
    name="email"
    autocomplete="email"
    aria-describedby="email-hint email-error"
    required
  />
  <span id="email-hint">Введіть робочу адресу</span>
  <span id="email-error" role="alert">Невірний формат email</span>
</div>

<!-- ❌ Неправильно — placeholder замість label -->
<input type="email" placeholder="Email" />
```

## Testing Checklist (Перед Здачею)

```bash
# 1. Lighthouse Accessibility audit (Chrome DevTools)
# 2. Tab через всю сторінку — чи все видно?
# 3. VoiceOver (macOS: Cmd+F5) — прочитай сторінку
# 4. Збільши шрифт до 200% — чи не ламається layout?
# 5. Увімкни Reduce Motion (System Settings) — перевір анімації
# 6. Переключи на Dark Mode — перевір контраст
# 7. Відключи мишку — чи можна пройти тільки з клавіатури?
```

## Common Failures (Виправ Негайно)

- ❌ `outline: none` без альтернативи
- ❌ `<div onclick="...">` замість `<button>`
- ❌ `placeholder` замість `<label>`
- ❌ `color: #ccc` на білому фоні (контраст ~1.8)
- ❌ Кастомний select без ARIA
- ❌ Модалка без focus trap
- ❌ Infinite scroll без кнопки «завантажити ще»
- ❌ Carousel без pause/stop
