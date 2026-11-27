---
name: install-into-my-stack
description: Help a user install LomboSaga next to their own Jellyfin server and verify it with doctor. Use when someone asks to set it up, install it, or add it to their compose file or server.
---

# Install LomboSaga into the user's stack

Ask, one question at a time, and use their answers (never assume a layout):

1. **How do you run Jellyfin?** Docker compose, a single `docker run`, or installed directly on the machine?
   - Compose: add the `lombo-saga` service from `compose.example.yaml` to their file and join Jellyfin's network, so the URL can be `http://<jellyfin service name>:8096`.
   - Docker run or direct install: use the machine's address and port instead, e.g. `http://192.0.2.10:8096` (use their real one, only in their own `.env`).
2. **Create an API key:** Jellyfin, Dashboard, API Keys, +. Name it after the app. One key per app.
3. **Optional alerts:** do they have a Discord, Slack or similar webhook? Leave `LOMBO_SAGA_WEBHOOK_URL` empty if not.
4. **Write `.env`** from `.env.example`. Keep `LOMBO_SAGA_DRY_RUN=true`. `.env` is git-ignored; never print the key back.
5. **Start it and run the check:** `docker compose up -d`, then `docker compose exec lombo-saga lombo-saga doctor`. Every line must say `ok`.
6. **Show what it would do:** `lombo-saga plan`. Walk through the output with the user.
7. **Go live only when they say so:** set `LOMBO_SAGA_DRY_RUN=false`, restart, and tell them where the logs are (`docker compose logs lombo-saga`).

If `doctor` fails, read the `troubleshoot` skill.
