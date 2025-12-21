from typing import Any, List, Dict
from core.models import Event, Agent
import random

class ChaosContainmentDyad:
    """
    Sample Dyad: Sentinel + Wildcard
    Synergy: 'Containment Field'
    If Wildcard causes too much chaos (hits someone), Sentinel cleans it up (restores stamina/order).
    """

    @staticmethod
    def check_requirements(roster: Dict[str, Agent]) -> bool:
        return "Sentinel-02" in roster and "Wildcard-04" in roster

    def __init__(self):
        pass

    def on_turn_start(self, ctx: Any) -> List[Event]:
        return []

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        events = []
        
        # If Wildcard lands a hit...
        if thrower_id == "Wildcard-04":
            # Sentinel has 50% chance to stabilize
            if random.random() < 0.5:
                sentinel = ctx.roster.get("Sentinel-02")
                wildcard = ctx.roster.get("Wildcard-04")
                
                if sentinel and wildcard:
                    # Wildcard gets "stabilized" (reduced chaos, boosted Dodge)
                    wildcard.dodge_mod *= 1.1
                    
                    events.append(Event(
                        tick=ctx.tick, 
                        thrower="Sentinel-02", 
                        intended="Wildcard-04", 
                        outcome="CONTAINMENT_FIELD",
                        actual="Stabilized", 
                        notes="Sentinel reinforces Wildcard's structure.",
                        tags=["dyad:chaos-containment"]
                    ))
                    
        return events
        
    def on_target_selected(self, ctx: Any, thrower_id: str, target_id: str) -> None:
        pass

    def on_turn_end(self, ctx: Any) -> List[Event]:
        return []
