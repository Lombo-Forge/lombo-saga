"""Command line: doctor, plan, run. Talks to the outside world; core.py decides.

lombo-saga doctor        check the settings and that Jellyfin answers; exit 1 on any failure
lombo-saga plan          show what would happen; changes nothing, ever
lombo-saga run [--loop]  do it (alerts only when DRY_RUN=false); --loop repeats every INTERVAL_SECONDS
"""

import argparse
import os
import sys
import time
from collections.abc import Callable

from . import __version__, core, notify
from .config import Config, ConfigError, from_env
from .jellyfin import Jellyfin, JellyfinError


def doctor(cfg: Config) -> int:
    jf = Jellyfin(cfg.jellyfin_url, cfg.jellyfin_api_key)
    ok = True

    def reachable() -> str:
        info = jf.public_info()
        return f"{info.get('ServerName')} {info.get('Version')}"

    def key_accepted() -> str:
        jf.info()
        return "yes"

    checks: list[tuple[str, Callable[[], str]]] = [
        ("Jellyfin reachable", reachable),
        ("API key accepted", key_accepted),
    ]
    for label, check in checks:
        try:
            print(f"[ ok ] {label}: {check()}")
        except JellyfinError as e:
            print(f"[FAIL] {label}: {e}")
            ok = False
    print(f"[ ok ] webhook: {'set' if cfg.webhook_url else 'not set (alerts are skipped)'}")
    print(f"[ ok ] mode: {'dry run (nothing is changed)' if cfg.dry_run else 'LIVE'}")
    return 0 if ok else 1


def plan(cfg: Config) -> int:
    actions = core.decide(Jellyfin(cfg.jellyfin_url, cfg.jellyfin_api_key).libraries())
    print("\n".join(str(a) for a in actions) or "Nothing to do.")
    return 0


def run_once(cfg: Config) -> int:
    actions = core.decide(Jellyfin(cfg.jellyfin_url, cfg.jellyfin_api_key).libraries())
    for a in actions:
        print(a)
    if actions and not cfg.dry_run and cfg.webhook_url:
        notify.send(cfg.webhook_url, "\n".join(str(a) for a in actions))
    return 0


def main(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lombo-saga", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("plan")
    run = sub.add_parser("run")
    run.add_argument("--loop", action="store_true")
    args = p.parse_args(argv)

    try:
        cfg = from_env(dict(os.environ) if env is None else env)
    except ConfigError as e:
        print(f"[FAIL] settings: {e}", file=sys.stderr)
        return 2

    try:
        if args.cmd == "doctor":
            return doctor(cfg)
        if args.cmd == "plan":
            return plan(cfg)
        while True:
            try:
                run_once(cfg)
            except (JellyfinError, notify.NotifyError) as e:
                print(f"[FAIL] {e}", file=sys.stderr)  # a loop survives one bad round
                if not args.loop:
                    return 1
            if not args.loop:
                return 0
            time.sleep(cfg.interval_seconds)
    except JellyfinError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
