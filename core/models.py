from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Agent:
    name: str
    accuracy: float = 0.55
    dodge: float = 0.25
    chaos: float = 0.0
    landed: int = 0
    taken: int = 0
    
    # Flavor
    traits: List[str] = field(default_factory=list)
    description: str = ""

    # Ace spite
    spite_meter: float = 0.0
    spite_gain_on_hit: float = 0.0
    spite_decay_per_turn: float = 0.0
    spite_max_bonus: float = 0.0
    spite_min_multiplier: float = 1.0

    # Janus paradox
    paradox_chance: float = 0.0
    paradox_budget: int = 0
    untouchable_while_budget: bool = False

    # Quinn stray magnet
    stray_magnet: float = 0.0

    # Kryssie beer mode
    holding_beer: bool = False
    beer_dodge_bonus: float = 0.0
    beer_dodge_bonus_step: float = 0.0
    beer_dodge_bonus_cap: float = 0.0

    # Transient Modifiers (Reset every turn)
    accuracy_mod: float = 1.0
    dodge_mod: float = 1.0
    
    # Phase 8: Ontological Frame
    frame: str = "COMBAT"  # "COMBAT" | "ONTOLOGICAL"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Agent:
        # Safety: Filter data keys to match class fields only
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

@dataclass
class Event:
    tick: int
    thrower: str
    intended: str
    outcome: str
    actual: str
    notes: str
    roll_hit: float
    roll_ricochet: float
    p_hit: float
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

