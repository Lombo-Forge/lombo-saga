"""The decisions. Pure: no network, no disk, no clock, so tests need no fakes.

This example looks at Jellyfin's libraries and flags any with no folders. Replace decide()
with your app's real rules, keep it pure, and let cli.py do the talking to the outside world.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Action:
    kind: str  # "warn" here; a real app might use "move", "stop", "retry"...
    target: str
    reason: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.target} ({self.reason})"


def decide(libraries: list[dict[str, Any]]) -> list[Action]:
    actions: list[Action] = []
    for lib in libraries:
        if not lib.get("Locations"):
            actions.append(Action("warn", lib.get("Name", "(unnamed)"), "library has no folders"))
    return actions
