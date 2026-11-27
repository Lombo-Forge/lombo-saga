---
name: install-into-my-stack
description: Help a user install LomboSaga next to their own Kavita and verify it with doctor. Use when someone asks to set it up, install it, or add it to their compose file or server.
---

# Install LomboSaga into the user's stack

Ask, one question at a time, and use their answers (never assume a layout):

1. **How do you run Kavita?** For compose, add the service from `compose.example.yaml` and join its network. Otherwise use the machine's address and port, only in their own `.env`.
2. **API key:** from an admin account's settings. It has full rights; keep it private.
3. **Which series belong together?** Write `rules.json` with them. Ask how books are foldered before using `authors`.
4. **Optional alerts:** a webhook, or leave it empty.
5. **Write `.env`** from `.env.example`. Keep `LOMBO_SAGA_DRY_RUN=true`.
6. **Start and check:** `docker compose up -d --build`, then `lombo-saga doctor` inside it.
7. **Show `lombo-saga plan`** and fix the rules together, then set `LOMBO_SAGA_DRY_RUN=false` only when they say so.

If `doctor` fails, read the `troubleshoot` skill.
