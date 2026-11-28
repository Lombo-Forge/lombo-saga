"""Command line: doctor, plan, run. Talks to the outside world; core.py decides.

lombo-saga doctor        check the settings, the rules file and Kavita; exit 1 on any failure
lombo-saga plan          show what would be added; changes nothing, ever
lombo-saga run [--loop]  do it (changes only when DRY_RUN=false); --loop repeats every INTERVAL_SECONDS
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from . import __version__, core, notify
from .api import ApiError, Kavita
from .config import Config, ConfigError, from_env


def load_rules(path: str) -> list[core.Rule]:
    """Read every round, so an edit applies without a restart. A bad file stops the round."""
    try:
        return core.parse_rules(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        raise core.RuleError(f"rules file {path}: {e}") from e


def run_once(cfg: Config, change: bool) -> int:
    """One round. change=False (plan, or dry run) writes and alerts nothing. Returns failures."""
    rules = load_rules(cfg.rules_file)
    kavita = Kavita(cfg.kavita_url, cfg.kavita_api_key)
    series = kavita.series()
    if not series:  # an empty answer is not "no books": change nothing
        print("[WARN] Kavita lists no series; nothing changed")
        return 0
    names = {int(s["id"]): str(s.get("name")) for s in series}
    collections = kavita.collections()
    added: list[str] = []
    failures = pending = 0
    for rule in rules:
        try:
            ids = core.wanted(series, rule)
            if not ids:
                continue
            cid, problem = core.find(collections, rule.title)
            if problem:
                print(f"[WARN] {rule.title}: left alone, {problem}", file=sys.stderr)
                continue
            current = {int(s["id"]) for s in kavita.series(cid)} if cid else set()
            missing = [i for i in ids if i not in current]
            if not missing:
                continue
            pending += 1
            verb = "add to" if cid else "create"
            line = f"{rule.title}: +{len(missing)} ({', '.join(names[i] for i in missing)})"
            if not change:
                print(f"would {verb} {line}")
                continue
            kavita.add(rule.title, missing, cid or 0)
            print(f"{'added to' if cid else 'created'} {line}")
            added.append(line)
            if not cid and cfg.promote:
                _promote(kavita, rule.title)
        except ApiError as e:
            failures += 1
            print(f"[FAIL] {rule.title}: {e}", file=sys.stderr)
    if not pending and not failures:
        print("Nothing to add.")
    if added and cfg.webhook_url:
        notify.send(cfg.webhook_url, "Collections updated:\n" + "\n".join(added)[:1500].replace("@", "@​"))
    return failures


def _promote(kavita: Kavita, title: str) -> None:
    collections = kavita.collections()
    new_id, _ = core.find(collections, title)
    for c in collections:
        if c.get("id") == new_id:
            kavita.promote(c)
            return
    print(f"[WARN] {title}: made, but not found again to make it visible to everyone", file=sys.stderr)


def doctor(cfg: Config) -> int:
    ok = True
    try:
        print(f"[ ok ] rules: {len(load_rules(cfg.rules_file))} in {cfg.rules_file}")
    except core.RuleError as e:
        print(f"[FAIL] {e}")
        ok = False
    kavita = Kavita(cfg.kavita_url, cfg.kavita_api_key)
    try:
        account = kavita.account()
        print(f"[ ok ] Kavita: key accepted for {account.get('username')}")
        if "Admin" not in (account.get("roles") or []):
            print("[WARN] this account is not an admin: it may not see every library or share a collection")
        print(f"[ ok ] series: {len(kavita.series())}")
    except ApiError as e:
        print(f"[FAIL] {e}")
        ok = False
    print(f"[ ok ] webhook: {'set' if cfg.webhook_url else 'not set (alerts are skipped)'}")
    print(f"[ ok ] mode: {'dry run (nothing is changed)' if cfg.dry_run else 'LIVE'}")
    return 0 if ok else 1


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

    if args.cmd == "doctor":
        return doctor(cfg)
    change = args.cmd == "run" and not cfg.dry_run
    loop = args.cmd == "run" and args.loop
    while True:
        try:
            failures = run_once(cfg, change)
        except Exception as e:  # noqa: BLE001  a loop survives one bad round, an odd reply included
            print(f"[FAIL] {e}", file=sys.stderr)
            failures = 1
        if not loop:
            return 1 if failures else 0
        time.sleep(cfg.interval_seconds)


if __name__ == "__main__":
    sys.exit(main())
