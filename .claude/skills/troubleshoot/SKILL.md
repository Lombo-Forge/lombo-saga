---
name: troubleshoot
description: Diagnose LomboSaga problems from doctor output and logs. Use when the app fails to start, doctor shows FAIL, alerts do not arrive, or it does nothing.
---

# Troubleshoot LomboSaga

Start with `lombo-saga doctor`. Each line says what failed.

| You see | It means | Fix |
|---|---|---|
| `[FAIL] settings: LOMBO_SAGA_X ...` (exit 2) | A setting is missing or invalid. | Fix it in `.env`; restart. |
| `rules file ...` | `rules.json` is missing or not valid. | The message says what; compare with `rules.example.json`. |
| `Kavita ...: HTTP 401` | Wrong API key. | Copy it again. |
| `... urlopen error` | The URL is not reachable from the container. | Use the service name or LAN address; check the shared network. |
| `HTTP 301` or `302` | The URL redirects. | Use the final address. |
| Plan shows nothing | Nothing matches, or it is already in the collection. | Check the series names in Kavita and the folder names for `authors`. |
| `left alone, 2 collections have this name` | Doubled collection. | Merge or rename one. |
| `this account is not an admin` | The key is a normal user's. | Use an admin's key. |

Logs: `docker compose logs --tail 100 lombo-saga`. In loop mode a failed round is logged and the next
one still runs, so look for `[FAIL]` lines. When you report a bug, include `doctor` output with the
key and webhook URL removed.
