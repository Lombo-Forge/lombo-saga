import pytest

from lombo_saga import core, notify
from lombo_saga.cli import main
from lombo_saga.config import ConfigError, from_env
from lombo_saga.jellyfin import Jellyfin, JellyfinError


def test_config_defaults_are_safe(env):
    cfg = from_env(env)
    assert cfg.dry_run is True
    assert cfg.interval_seconds == 3600


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("LOMBO_SAGA_JELLYFIN_URL", "jellyfin:8096"),
        ("LOMBO_SAGA_JELLYFIN_API_KEY", "changeme"),
        ("LOMBO_SAGA_WEBHOOK_URL", "ftp://x"),
        ("LOMBO_SAGA_INTERVAL_SECONDS", "5"),
        ("LOMBO_SAGA_INTERVAL_SECONDS", "soon"),
    ],
)
def test_config_rejects_bad_values_and_names_the_setting(env, name, value):
    with pytest.raises(ConfigError, match=name):
        from_env({**env, name: value})


def test_decide_is_pure_and_flags_empty_libraries():
    acts = core.decide([{"Name": "A", "Locations": ["/x"]}, {"Name": "B", "Locations": []}])
    assert [a.target for a in acts] == ["B"]
    assert core.decide([]) == []


def test_client_sends_the_key_and_reports_failures(fake):
    assert Jellyfin(fake.url, "good-key").libraries()[0]["Name"] == "Movies"
    assert fake.requests[-1]["auth"] == 'MediaBrowser Token="good-key"'
    with pytest.raises(JellyfinError, match="HTTP 401"):
        Jellyfin(fake.url, "wrong").info()
    with pytest.raises(JellyfinError):
        Jellyfin("http://127.0.0.1:1", "k", timeout=1).public_info()


def test_notify_posts_json(fake):
    notify.send(fake.url + "/hook", "hello")
    assert fake.posts()[0]["body"] == {"content": "hello", "text": "hello"}
    with pytest.raises(notify.NotifyError):
        notify.send("http://127.0.0.1:1/hook", "x", timeout=1)


def test_doctor_passes_and_fails(env, fake, capsys):
    assert main(["doctor"], env) == 0
    assert "[FAIL]" not in capsys.readouterr().out
    assert main(["doctor"], {**env, "LOMBO_SAGA_JELLYFIN_API_KEY": "wrong"}) == 1
    assert "API key accepted: /System/Info: HTTP 401" in capsys.readouterr().out


def test_bad_settings_exit_2(capsys):
    assert main(["plan"], {}) == 2
    assert "LOMBO_SAGA_JELLYFIN_URL" in capsys.readouterr().err


def test_plan_never_posts_and_run_is_quiet_while_dry(env, fake, capsys):
    assert main(["plan"], env) == 0
    assert "warn: Empty" in capsys.readouterr().out
    assert main(["run"], env) == 0
    assert fake.posts() == []


def test_run_alerts_only_when_live(env, fake):
    assert main(["run"], {**env, "LOMBO_SAGA_DRY_RUN": "false"}) == 0
    assert "Empty" in fake.posts()[0]["body"]["content"]
