---
name: troubleshoot
description: Diagnose LomboSaga problems from doctor output and logs. Use when the app fails to start, doctor shows FAIL, alerts do not arrive, or it does nothing.
---

# Troubleshoot LomboSaga

Start with `lombo-saga doctor`. Each line says what failed.

| You see | It means | Fix |
|---|---|---|
| `[FAIL] settings: LOMBO_SAGA_X ...` (exit 2) | A setting is missing or invalid. The message names it. | Fix that variable in `.env`; restart the container. |
| `Jellyfin reachable: ... <urlopen error>` | The app cannot reach Jellyfin at that URL. | From inside the container the URL is not the one in your browser. Use the compose service name or the machine's LAN address; check the port and the shared network. |
| `API key accepted: /System/Info: HTTP 401` | Jellyfin refused the key. | Create a new key (Dashboard, API Keys) and update `.env`. |
| `HTTP 404` on a path | Your Jellyfin version has no such endpoint. | Check `https://your-server/api-docs/swagger`; adjust `jellyfin.py`. |
| Doctor is fine but nothing alerts | Dry run is on, the webhook is empty, or `plan` has nothing to report. | Run `plan`. Set `LOMBO_SAGA_DRY_RUN=false` only when ready. Check the webhook line in `doctor`. |
| `webhook failed` | The webhook URL rejects the message. | Test it with `curl -X POST -H 'Content-Type: application/json' -d '{"content":"test"}' <url>`. |

Logs: `docker compose logs --tail 100 lombo-saga`. In loop mode a failed round is logged and the next
one still runs, so look for `[FAIL]` lines. When you report a bug, include `doctor` output with the
key and webhook URL removed.
