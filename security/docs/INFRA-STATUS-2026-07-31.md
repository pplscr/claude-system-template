# INFRA-STATUS-2026-07-31 — Стан інфраструктури

**Дата:** 2026-07-31
**Виконавець:** infra-guardian (агент простору security)
**Обʼєкт:** vuzol (100.84.177.33, Ubuntu 24.04) + mac-mini (M4, macOS 15.5)
**Загальний стан:** ✅ OK — всі цільові сервіси працюють, auth у нормі.

---

## 1. Цільові перевірки (задача)

| # | Перевірка | Команда | Результат | Статус |
|---|-----------|---------|-----------|--------|
| 1 | Qdrant check | `ssh vuzol /root/scripts/qdrant-check.sh` | `Qdrant: 11 collections` | ✅ OK |
| 2a | Task API без auth | `curl -s -o /dev/null -w %{http_code} :8000/tasks` | `401` (очікувано) | ✅ OK |
| 2b | Task API з auth | `curl -H 'X-API-Key: merzota24' :8000/tasks` | `11` проєктів | ✅ OK |
| 3 | cc-connect | `systemctl is-active cc-connect && journalctl -n 2` | `active`, логи в нормі | ✅ OK |

---

## 2. Розширений healthcheck

### Сервіси (systemctl)

| Сервіс | Статус |
|--------|--------|
| ssh | ✅ active |
| task-api | ✅ active |
| cc-connect | ✅ active |
| postgresql@16-main | ✅ active |

### Failed units

| Unit | Статус | Примітка |
|------|--------|----------|
| certbot.service | ⚠️ failed | Відомий баг Python-скрипта, не повʼязаний зі змінами (зафіксовано в ZVIT) |
| memory-sleep.service | ⚠️ failed | Потребує API key (зафіксовано в ZVIT) |

Обидва — відомі, не впливають на цільові сервіси.

### Ресурси

| Ресурс | Значення | Оцінка |
|--------|----------|--------|
| Uptime | 6 днів, 45 хв | ✅ стабільно |
| Load average | 0.04 / 0.05 / 0.09 | ✅ низький |
| RAM | 2.3G / 7.6G (5.3G available) | ✅ |
| Swap | 38M / 15G | ✅ |
| Disk `/` | 53G / 75G = **73%** | ⚠️ моніторити (було 72%) |

### Docker (7 контейнерів, всі running)

| Контейнер | Статус | Порти |
|-----------|--------|-------|
| litellm | ✅ Up 18 хв | 0.0.0.0:4000 |
| vaultwarden | ✅ Up 44h (healthy) | 127.0.0.1:8081 |
| dozzle | ✅ Up 44h | 0.0.0.0:8080 |
| uptime-kuma | ✅ Up 44h (healthy) | 0.0.0.0:3001 |
| beszel | ✅ Up 44h | 0.0.0.0:8090 |
| beszel-agent | ✅ Up 3h | — |
| merezha-qdrant | ✅ Up 45h | 0.0.0.0:6333-6334 |

Порти `0.0.0.0` — штатно, публічний доступ блокується iptables DOCKER-USER (Layer 3 захисту).

### Tailscale mesh

| Вузол | Статус |
|-------|--------|
| mac-mini (100.127.88.114) | ✅ active, direct |
| vuzol (100.84.177.33) | ✅ active, direct |
| desktop-vot8vnc (100.78.19.35) | ⚠️ offline 24 дні |

### Task API health

`GET :8000/health` → `{"status": "ok"}` ✅

---

## 3. Спостереження

1. **litellm рестартнувся 18 хв тому** — інші контейнери працюють 44-45h. Варто перевірити журнал litellm (docker logs) при наступному вході, але сервіс зараз активний.
2. **Диск 73%** (+1% від попереднього аудиту). У ZVIT зафіксовано 15G на докази NSC — продовжувати моніторити.
3. **desktop-vot8vnc offline 24 дні** — застарілий вузол, ACL Tailnet має його обмежувати. Не загроза, але можна розглянути видалення з mesh, якщо більше не потрібен.
4. **certbot + memory-sleep failed** — відомі, зафіксовані в ZVIT як acceptable ризики.

---

## 4. Висновок

Всі 4 цільові сервіси (Qdrant, Task API auth, cc-connect, health) працюють коректно.
Auth Task API підтверджено: без ключа 401, з ключем — 11 проєктів.
Серверна інфраструктура стабільна, 6 днів аптайму, низьке навантаження.

**Статус: ✅ OK** — критичних проблем немає.

---

## 5. Рекомендації

| # | Рекомендація | Пріоритет |
|---|--------------|-----------|
| 1 | Перевірити docker logs litellm після рестарту (18 хв) | LOW |
| 2 | Моніторити диск 73% → тримати <80% | MEDIUM |
| 3 | Розглянути видалення desktop-vot8vnc з Tailscale (offline 24d) | LOW |
| 4 | Щотижневий healthcheck за SPACE.md (уже в розкладі) | — |
