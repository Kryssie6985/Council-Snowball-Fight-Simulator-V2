from typing import Any, List, Dict
from core.models import Event, Agent

class CustomDyadTemplate:
    """
    A template for creating custom dyads.
    Rename this class and implement the logic below.
    """

    @staticmethod
    def check_requirements(roster: Dict[str, Agent]) -> bool:
        """
        Return True if this Dyad should be active for the given roster.
        Example: return "Batman" in roster and "Robin" in roster
        """
        return False

    def __init__(self):
        # Initialize any internal state here
        self.combo_counter = 0

    def on_turn_start(self, ctx: Any) -> List[Event]:
        """
        Called at the start of every turn.
        Use this to apply passive buffs or check cooldowns.
        """
        return []

    def on_target_selected(self, ctx: Any, thrower_id: str, target_id: str) -> None:
        """
        Called when a thrower selects a target.
        Use this to track who is targeting whom.
        """
        pass

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        """
        Called when a hit occurs.
        Return a list of Events to log special effects.
        """
        # Example:
        # if thrower_id == "Batman" and target_id == "Joker":
        #     return [Event(..., outcome="JUSTICE_SERVED", ...)]
        return []

    def on_turn_end(self, ctx: Any) -> List[Event]:
        """
        Called at the end of the turn.
        Use this to decay counters or reset temporary states.
        """
        return []

    def check_interception(self, ctx: Any, thrower_id: str, target_id: str, rng: Any) -> str | None:
        """
        Optional: Return a new target_id to intercept the throw.
        Return None for no interception.
        """
        return None
