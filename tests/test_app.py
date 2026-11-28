import json
import re
from pathlib import Path

import pytest

from conftest import book
from lombo_saga import core, notify
from lombo_saga.api import ApiError, Kavita
from lombo_saga.cli import main
from lombo_saga.config import ConfigError, from_env

ROOT = Path(__file__).parent.parent
LIVE = {"LOMBO_SAGA_DRY_RUN": "false"}


def test_names_match_without_case_and_authors_must_be_a_whole_folder():
    rule = core.Rule("Red", ("red tower*",), ("ann author",))
    assert core.matches(book(1, "Red Tower"), rule)
    assert not core.matches(book(1, "Blue Lake"), rule)
    assert not core.matches(book(1, "Red Tower", "Joann Author"), rule)
    assert core.matches({"id": 1, "name": "X", "localizedName": "Red Tower"}, core.Rule("R", ("Red Tower",)))


@pytest.mark.parametrize(
    "raw",
    [{}, [], {"A": []}, {"A": "x"}, {"A": ["*"]}, {"": ["x"]}, {"A": {"names": ["x"], "author": ["y"]}}, {"A": [1]}],
)
def test_bad_rules_are_refused(raw):
    with pytest.raises(core.RuleError):
        core.parse_rules(raw)


def test_the_example_rules_load():
    assert len(core.parse_rules(json.loads((ROOT / "rules.example.json").read_text()))) == 2


def test_find_leaves_doubled_and_synced_collections_alone():
    assert core.find([], "Red") == (None, None)
    assert core.find([{"id": 4, "title": "RED"}], "Red") == (4, None)
    assert core.find([{"id": 4, "title": "Red"}, {"id": 5, "title": "Red"}], "Red")[1]
    assert core.find([{"id": 4, "title": "Red", "source": 1}], "Red")[1]


def test_plan_and_dry_run_change_nothing(env, fake, capsys):
    assert main(["plan"], {**env, **LIVE}) == 0
    assert main(["run"], env) == 0
    assert "would create Red: +2 (Red Tower, Red Tower Returns)" in capsys.readouterr().out
    assert fake.writes() == []


def test_live_run_creates_shares_then_only_adds_what_is_new(env, fake, capsys):
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.members == {1: {1, 2}}
    assert fake.collections[0]["promoted"] is True
    assert "Nothing to add" not in capsys.readouterr().out
    fake.calls.clear()
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.writes() == []
    assert "Nothing to add." in capsys.readouterr().out
    fake.members[1].add(3)  # added by hand: stays
    fake.series.append(book(4, "Red Tower Falls"))
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.members == {1: {1, 2, 3, 4}}
    assert len(fake.collections) == 1


def test_promote_can_be_off_and_an_existing_collection_is_never_updated(env, fake):
    assert main(["run"], {**env, **LIVE, "LOMBO_SAGA_PROMOTE": "false"}) == 0
    assert fake.collections[0]["promoted"] is False
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.collections[0]["promoted"] is False


def test_an_empty_library_changes_nothing(env, fake):
    fake.series = []
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.writes() == []


def test_one_failing_rule_does_not_stop_the_others(env, fake):
    Path(env["LOMBO_SAGA_RULES_FILE"]).write_text(json.dumps({"Bad": ["Red Tower"], "Good": ["Red Tower*"]}))
    fake.fail_titles = {"Bad"}
    assert main(["run"], {**env, **LIVE}) == 1
    assert [c["title"] for c in fake.collections] == ["Good"]


def test_every_page_of_series_is_read(env, fake):
    fake.series = [book(i, f"Red Tower {i}") for i in range(1, 451)]
    assert main(["run"], {**env, **LIVE}) == 0
    assert len(fake.members[1]) == 450
    fake.calls.clear()
    assert main(["run"], {**env, **LIVE}) == 0
    assert fake.writes() == []


def test_a_broken_rules_file_stops_the_round(env, fake, capsys):
    Path(env["LOMBO_SAGA_RULES_FILE"]).write_text("{not json")
    assert main(["run"], {**env, **LIVE}) == 1
    assert "rules file" in capsys.readouterr().err
    assert main(["doctor"], env) == 1


def test_doctor(env, fake, capsys):
    assert main(["doctor"], env) == 0
    assert "[WARN]" not in capsys.readouterr().out
    fake.roles = ["Login"]
    assert main(["doctor"], env) == 0
    assert "not an admin" in capsys.readouterr().out
    assert main(["doctor"], {**env, "LOMBO_SAGA_KAVITA_API_KEY": "wrong"}) == 1


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("KAVITA_URL", "kavita:5000"),
        ("KAVITA_API_KEY", "changeme"),
        ("WEBHOOK_URL", "ftp://x"),
        ("INTERVAL_SECONDS", "5"),
        ("INTERVAL_SECONDS", "soon"),
        ("PROMOTE", "maybe"),
        ("DRY_RUN", "treu"),
    ],
)
def test_config_rejects_bad_values_and_names_the_setting(env, name, value):
    with pytest.raises(ConfigError, match=f"LOMBO_SAGA_{name}"):
        from_env({**env, f"LOMBO_SAGA_{name}": value})


def test_bad_settings_exit_2_and_env_example_is_complete(capsys):
    assert main(["plan"], {}) == 2
    assert "LOMBO_SAGA_KAVITA_URL" in capsys.readouterr().err
    listed = set(re.findall(r"^LOMBO_SAGA_(\w+)=", (ROOT / ".env.example").read_text(), re.M))
    config = (ROOT / "src/lombo_saga/config.py").read_text()
    assert listed == set(re.findall(r'get\("([A-Z_]+)"', config))


def test_client_and_webhook_failures(fake):
    with pytest.raises(ApiError, match="HTTP 401"):
        Kavita(fake.url, "wrong").collections()
    with pytest.raises(ApiError):
        Kavita("http://127.0.0.1:1", "k", timeout=1).account()
    notify.send(fake.url + "/hook", "hello")
    assert fake.calls[-1]["body"]["content"] == "hello"
    with pytest.raises(notify.NotifyError):
        notify.send("http://127.0.0.1:1/hook", "x", timeout=1)
