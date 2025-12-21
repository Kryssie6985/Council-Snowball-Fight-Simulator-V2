from typing import Any, List, Dict
from core.models import Event, Agent

class OffensiveLineDyad:
    """
    Sample Dyad: Vanguard + Striker
    Synergy: 'Avenger Protocol'
    If Vanguard (the tank) gets hit, Striker (the DPS) gains an accuracy buff.
    """

    @staticmethod
    def check_requirements(roster: Dict[str, Agent]) -> bool:
        return "Vanguard-01" in roster and "Striker-03" in roster

    def __init__(self):
        self.avenger_stacks = 0

    def on_turn_start(self, ctx: Any) -> List[Event]:
        # Decay stacks slowly
        if self.avenger_stacks > 0:
            self.avenger_stacks = max(0, self.avenger_stacks - 1)
        
        # Apply buff if stacks exist
        if self.avenger_stacks > 0:
            striker = ctx.roster.get("Striker-03")
            if striker:
                # 5% accuracy per stack
                multiplier = 1.0 + (0.05 * self.avenger_stacks)
                striker.accuracy_mod *= multiplier
                
        return []

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        events = []
        
        # If Vanguard takes a hit...
        if target_id == "Vanguard-01":
            self.avenger_stacks += 2
            events.append(Event(
                tick=ctx.tick, 
                thrower="System", 
                intended="Striker-03", 
                outcome="AVENGER_PROTOCOL",
                actual="Buff", 
                notes=f"Striker enraged! Stacks: {self.avenger_stacks}",
                tags=["dyad:offensive-line"]
            ))
            
        return events
        
    def on_target_selected(self, ctx: Any, thrower_id: str, target_id: str) -> None:
        pass

    def on_turn_end(self, ctx: Any) -> List[Event]:
        return []
