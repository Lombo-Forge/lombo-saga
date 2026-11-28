<p align="center"><img src="assets/banner.svg" alt="LomboSaga" width="100%"></p>

<p align="center">
  <a href="LICENSE"><img alt="License: GPL-3.0" src="https://img.shields.io/github/license/Lombo-Forge/lombo-saga"></a>
  <a href="https://github.com/Lombo-Forge/lombo-saga/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/Lombo-Forge/lombo-saga/ci.yml?branch=main&label=CI"></a>
  <a href="https://github.com/Lombo-Forge/lombo-saga/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://img.shields.io/github/actions/workflow/status/Lombo-Forge/lombo-saga/codeql.yml?branch=main&label=CodeQL"></a>
  <a href="https://github.com/Lombo-Forge/lombo-saga/releases"><img alt="Release" src="https://img.shields.io/github/v/release/Lombo-Forge/lombo-saga?include_prereleases"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-blue">
  <a href="https://ko-fi.com/datlombardo"><img alt="Support on Ko-fi" src="https://img.shields.io/badge/Ko--fi-support-FF5E5B?logo=ko-fi&logoColor=white"></a>
</p>

# LomboSaga

Keeps your [Kavita](https://github.com/Kareadita/Kavita) collections for book series filled. A series often shows up as several unrelated entries; you write one rule, and every matching book, including the next one you add, lands in the same collection.

> **Status:** checked against a throwaway Kavita 0.9.1 with a handful of test books, not yet against a large real library. Keep it in dry-run mode until `plan` shows what you expect.

```text
$ lombo-saga plan
would create Tower: +2 (Red Tower, Red Tower Returns)
would create Lake: +1 (Blue Lake)
```

## Contents

- [What it does and does not do](#what-it-does-and-does-not-do)
- [Rules](#rules)
- [Install in a minute](#install-in-a-minute)
- [Commands](#commands)
- [Settings](#settings)
- [Contributing and licence](#contributing-and-licence)

## What it does and does not do

Every round (hourly by default) it adds the series that match a rule to that rule's collection, creating the collection if needed.

- It only **adds**. It never takes a series out or deletes a collection, so what you arranged by hand stays. A series you remove by hand comes back while a rule still matches it.
- It only touches collections named in your rules.
- A collection it creates is made visible to everyone (`LOMBO_SAGA_PROMOTE=false` to stop that). Existing collections are not changed in any other way.
- A name used by two collections, or a collection synced from an outside service, is left alone.
- If Kavita lists no series, or the rules file is broken, nothing changes.

## Rules

Copy `rules.example.json` to `config/rules.json`:

```json
{
  "Red Tower": { "names": ["Red Tower*"], "authors": ["Ann Author"] },
  "Lake Stories": ["Blue Lake*", "Green Lake*"]
}
```

The key is the collection's name. `names` are matched against the series name, ignoring case, with `*` and `?` as wildcards (`[` and `]` are special too). `authors`, if given, must be one of the folders in the book's path, as in `Author/Title/book.epub`. The file is read again every round. Mount its folder, as `compose.example.yaml` does: a container that mounts only the file keeps reading the old copy after an editor or `git pull` replaces it.

## Install in a minute

1. In Kavita, copy the API key of an admin account.
2. Copy `.env.example` to `.env` and `rules.example.json` to `config/rules.json`, and fill both in.
3. Start it:
   ```sh
   docker compose -f compose.example.yaml up -d
   docker compose -f compose.example.yaml exec lombo-saga lombo-saga doctor
   ```

It starts in dry-run mode. Run `lombo-saga plan`, then set `LOMBO_SAGA_DRY_RUN=false` when you are happy.

## Commands

| Command | What it does |
|---|---|
| `lombo-saga doctor` | Checks settings, the rules file and Kavita. Exit code 1 if anything fails. |
| `lombo-saga plan` | Shows what would be added. Never changes anything. |
| `lombo-saga run [--loop]` | Does it. `--loop` repeats every `LOMBO_SAGA_INTERVAL_SECONDS`. |

## Settings

Everything is an environment variable, listed with defaults in [.env.example](.env.example). The API key has your account's full rights, so keep `.env` private.

## Contributing and licence

Contribution, security and conduct rules come from the [Lombo-Forge organisation](https://github.com/Lombo-Forge/.github). Licensed under [GPL-3.0](LICENSE). Credits are in [NOTICE.md](NOTICE.md). Not affiliated with or endorsed by the Kavita project.
