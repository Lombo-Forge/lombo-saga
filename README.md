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

Keeps Kavita collections for book series filled, from rules you write.

> **Status: skeleton, not built.** The code is still the template's example, so it does not do the above yet and there is
> nothing to install. The plan is in [docs/architecture.md](docs/architecture.md#what-it-will-do).

## Contents

- [What is here](#what-is-here)
- [Develop](#develop)
- [Contributing and licence](#contributing-and-licence)

## What is here

The Lombo-Forge starting point: settings from `LOMBO_SAGA_*` variables, `doctor`, a dry-run `plan`, webhook
alerts, tests against a fake server, a container and CI. It will need Kavita.

## Develop

```sh
pip install -e '.[dev]' && pytest -q --cov
```

## Contributing and licence

Contribution, security and conduct rules come from the [Lombo-Forge organisation](https://github.com/Lombo-Forge/.github). Licensed under [GPL-3.0](LICENSE). Credits are in [NOTICE.md](NOTICE.md). Not affiliated with or endorsed by the Jellyfin project.
