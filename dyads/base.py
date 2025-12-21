from typing import Any, List, Protocol
from core.models import Event

class Dyad(Protocol):
    """
    Protocol for a Dyad interaction module.
    Each method receives a context object (ctx) providing access to the roster/sim state.
    """
    def on_turn_start(self, ctx: Any) -> List[Event]:
        """Called at the start of a turn, after stats reset."""
        ...

    def on_target_selected(self, ctx: Any, thrower_id: str, target_id: str) -> None:
        """Called after a thrower has picked a target."""
        ...

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        """Called when a hit occurs."""
        ...

    def on_turn_end(self, ctx: Any) -> List[Event]:
        """Called at the end of the turn."""
        ...
