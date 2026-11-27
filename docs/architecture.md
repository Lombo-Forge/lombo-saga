# How it is built

## Contents

- [What it will do](#what-it-will-do)
- [The shape](#the-shape)
- [Why it is split this way](#why-it-is-split-this-way)
- [Safe by default](#safe-by-default)
- [Settings](#settings)
- [Alerts](#alerts)
- [Adding a Jellyfin call](#adding-a-jellyfin-call)

## What it will do

Planned, not built.

A series often shows up in Kavita as several unrelated entries. You write rules (a collection name, name patterns,
and optionally authors) and the app adds every matching series to that collection.

- It only ever **adds**. Anything you arranged by hand stays.
- It only touches the collections named in your rules.
- If Kavita cannot be read, or lists no series, nothing changes.
- Dry run first; `plan` shows what would be added.

The template's Jellyfin client is a placeholder here: the app talks to Kavita, not Jellyfin.

## The shape

```
Jellyfin  <--  jellyfin.py  -->  cli.py  -->  core.py (decides)
                                    |
                                    +-->  notify.py  -->  your webhook
```

`cli.py` fetches data, hands it to `core.decide()`, then acts on the answer. `core.py` never
touches the network, the disk or the clock.

## Why it is split this way

Rules are the part that changes most and breaks most quietly. Because `decide()` takes plain data
and returns plain data, a test is two lines and needs no server. The I/O layers are thin and are
tested once, against a fake Jellyfin on localhost (`tests/conftest.py`).

## Safe by default

- `DRY_RUN` is true until the person sets it to false.
- `plan` never changes anything and never alerts.
- `doctor` separates "Jellyfin is unreachable" from "the key was refused", so the fix is obvious.
- A bad setting stops the app at start-up and names the variable.
- In `--loop` mode one failed round is printed and the next one still runs.

## Settings

Every setting is an environment variable with the `LOMBO_SAGA_` prefix, validated in `config.py`.
To add one: read it in `config.py` with a clear error, add a line to `.env.example`, and add a test.

## Alerts

`notify.send(url, message)` posts JSON with the text under `content` and `text`, which Discord,
Slack and many bridges accept. Nothing is hard-coded to a service. If you want ntfy, Gotify or
email, run an Apprise-style bridge and point the webhook at it.

## Adding a Jellyfin call

Add a method to `Jellyfin` in `jellyfin.py` that calls `self._get(path)`, add the path to the
fake in `tests/conftest.py`, and test it. The Jellyfin API reference for your server version is at
`https://your-server/api-docs/swagger`. Check a new call against a throwaway Jellyfin before
relying on it.
