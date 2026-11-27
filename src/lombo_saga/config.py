"""Settings, read once from environment variables (see .env.example).

Every setting has a LOMBO_SAGA_ prefix so it never collides with another container's variables.
A bad value stops the app at start-up with a message that names the variable.
"""

from dataclasses import dataclass
from urllib.parse import urlparse

PREFIX = "LOMBO_SAGA_"


class ConfigError(Exception):
    """A setting is missing or invalid. The message says which one and what to do."""


@dataclass(frozen=True)
class Config:
    kavita_url: str
    kavita_api_key: str
    rules_file: str
    promote: bool
    webhook_url: str | None
    dry_run: bool
    interval_seconds: int


def _truthy(value: str, name: str) -> bool:
    """Strict on/off: a typo such as DRY_RUN=treu is an error, never a silent 'off'."""
    word = value.strip().lower()
    if word in {"1", "true", "yes", "on"}:
        return True
    if word in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{PREFIX}{name} must be true or false (got {value!r})")


def from_env(env: dict[str, str]) -> Config:
    def get(name: str, default: str = "") -> str:
        return (env.get(PREFIX + name) or "").strip() or default

    url = get("KAVITA_URL").rstrip("/")
    if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
        raise ConfigError(f"{PREFIX}KAVITA_URL must be a full URL such as http://kavita:5000 (got {url!r})")

    key = get("KAVITA_API_KEY")
    if key in {"", "changeme"}:
        raise ConfigError(f"{PREFIX}KAVITA_API_KEY is not set. Copy it from your Kavita account settings.")

    webhook = get("WEBHOOK_URL") or None
    if webhook and urlparse(webhook).scheme not in {"http", "https"}:
        raise ConfigError(f"{PREFIX}WEBHOOK_URL must start with http:// or https:// (or be empty)")

    try:
        interval = int(get("INTERVAL_SECONDS", "3600"))
    except ValueError:
        raise ConfigError(f"{PREFIX}INTERVAL_SECONDS must be a whole number of seconds") from None
    if interval < 60:
        raise ConfigError(f"{PREFIX}INTERVAL_SECONDS must be at least 60")

    return Config(
        kavita_url=url,
        kavita_api_key=key,
        rules_file=get("RULES_FILE", "/config/rules.json"),
        promote=_truthy(get("PROMOTE", "true"), "PROMOTE"),
        webhook_url=webhook,
        # Safe by default: nothing is changed until the person sets DRY_RUN=false.
        dry_run=_truthy(get("DRY_RUN", "true"), "DRY_RUN"),
        interval_seconds=interval,
    )
