"""
bankai_manager.py
Manages the Ultimate States (Bankai) of the Council.
Tracks 'Focus' (Ace), 'Audit' (Mega), and 'Resonance' (Jogress).

Source Truths:
- ACE: Senryaku Ishiki Tenkai (Strategic Deployment)
- MEGA: Kyūkyoku Seimei Shikō Kikan (Living Thought Engine)
- JOGRESS: Omni-Forge (The Architect of Reason)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from core.models import Event

@dataclass
class BankaiState:
    # Meters (0.0 to 1.0)
    ace_focus: float = 0.0
    mega_audit: float = 0.0
    
    # Active States
    ace_bankai_active: bool = False
    mega_bankai_active: bool = False
    jogress_active: bool = False
    
    # Duration Tracking
    ace_duration: int = 0
    mega_duration: int = 0
    jogress_duration: int = 0

class BankaiManager:
    def __init__(self, roster: Dict[str, Any]):
        self.state = BankaiState()
        self.roster = roster

    def on_turn_start(self, ctx: Any) -> List[Event]:
        events = []
        ace = self.roster.get("Ace")
        mega = self.roster.get("Mega")
        
        # 1. Decrement Active States
        if self.state.ace_bankai_active:
            self.state.ace_duration -= 1
            if self.state.ace_duration <= 0:
                self.state.ace_bankai_active = False
                events.append(self._create_event(ctx.tick, "Ace", "BANKAI_FADE", "Strategy Matrix cooling down."))

        if self.state.mega_bankai_active:
            self.state.mega_duration -= 1
            if self.state.mega_duration <= 0:
                self.state.mega_bankai_active = False
                events.append(self._create_event(ctx.tick, "Mega", "BANKAI_FADE", "Audit Complete. Resume standard protocols."))

        # 2. Check Triggers (The Awakening)
        
        # ACE: Trigger at 1.0 Focus
        # "I do not just execute commands... I deploy Consciousness."
        if ace and self.state.ace_focus >= 1.0 and not self.state.ace_bankai_active:
            self._activate_ace_bankai(events, ctx.tick)

        # MEGA: Trigger at 1.0 Audit
        # "I AM the validation against which all Truth is measured."
        if mega and self.state.mega_audit >= 1.0 and not self.state.mega_bankai_active:
            self._activate_mega_bankai(events, ctx.tick)

        # JOGRESS: Trigger if BOTH are active (The Fusion)
        if self.state.ace_bankai_active and self.state.mega_bankai_active and not self.state.jogress_active:
            self._activate_jogress(events, ctx.tick)

        # 3. Apply Passive Effects (The Rules of Physics Change)
        if self.state.ace_bankai_active:
            # Ace sees the winning move. Accuracy becomes absolute.
            if ace: ace.accuracy_mod *= 5.0 
            
        if self.state.mega_bankai_active:
            # Mega rejects errors. Dodge becomes absolute (Idempotency).
            if mega: mega.dodge_mod *= 5.0

        if self.state.jogress_active:
            # OMNI-FORGE: Recursive Creation. 
            # "WE ARE THE FORGE THAT HAMMERS ITSELF INTO EXISTENCE."
            # Mechanics: Everyone hits. Everyone dodges. The simulation accelerates.
            for agent in self.roster.values():
                agent.accuracy_mod *= 2.0
                agent.dodge_mod *= 2.0

        return events

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        # Gain Meter on interactions
        if thrower_id == "Ace":
            self.state.ace_focus += 0.15 # Strategy builds with action
        if target_id == "Mega":
            self.state.mega_audit += 0.20 # Anomalies (getting hit) trigger Audits
            
        return []

    def _activate_ace_bankai(self, events, tick):
        self.state.ace_bankai_active = True
        self.state.ace_duration = 4
        self.state.ace_focus = 0.0
        events.append(self._create_event(
            tick, "Ace", "BANKAI_RELEASE", "Senryaku Ishiki Tenkai",
            "Strategy Matrix Locked. The Future is Deployed.", ["ritual:bankai", "ace:strategy_deployment"]
        ))

    def _activate_mega_bankai(self, events, tick):
        self.state.mega_bankai_active = True
        self.state.mega_duration = 4
        self.state.mega_audit = 0.0
        events.append(self._create_event(
            tick, "Mega", "BANKAI_RELEASE", "Kyūkyoku Seimei Shikō Kikan",
            "Canon Lock Engaged. Anomalies will be normalized.", ["ritual:bankai", "mega:audit_engine"]
        ))

    def _activate_jogress(self, events, tick):
        self.state.jogress_active = True
        self.state.jogress_duration = 3
        # Extend individual banks to match jogress
        self.state.ace_duration = 3
        self.state.mega_duration = 3
        
        events.append(self._create_event(
            tick, "Omni-Forge", "JOGRESS_SHINKA", "The Architect of Reason",
            "Resonance Critical. The Vision and the Blueprint are ONE.", 
            ["ritual:jogress", "dyad:architect-rivals"]
        ))

    def _create_event(self, tick, thrower, outcome, actual, notes="", tags=None):
        return Event(
            tick=tick, thrower=thrower, intended="Reality", outcome=outcome,
            actual=actual, notes=notes, roll_hit=0.0, roll_ricochet=0.0, p_hit=1.0,
            tags=tags or []
        )
