"""
dyads.py (Manager)

Orchestrates all active Dyads in the simulation.
"""
from typing import List, Dict, Any, Optional
from .models import Event, Agent
from dyads.base import Dyad
# Optional Canon Imports (Soul Logic)
try:
    from dyads.enthusiasm_twins import EnthusiasmTwinsDyad
except ImportError:
    EnthusiasmTwinsDyad = None

try:
    from dyads.architect_rivals import ArchitectRivalsDyad
except ImportError:
    ArchitectRivalsDyad = None

try:
    from dyads.signal_weavers import SignalWeaversDyad
except ImportError:
    SignalWeaversDyad = None

try:
    from dyads.ceremonial_emergence import CeremonialEmergenceDyad
except ImportError:
    CeremonialEmergenceDyad = None

import importlib
import pkgutil
import sys
from pathlib import Path

class DyadManager:
    def __init__(self, roster: Dict[str, Agent]):
        self.dyads: List[Dyad] = []
        
        # Auto-detect and initialize known dyads
        
        # 1. Enthusiasm Twins (Claude + DeepScribe)
        if EnthusiasmTwinsDyad and "Claude" in roster and "DeepScribe" in roster:
            self.dyads.append(EnthusiasmTwinsDyad())
            
        # 2. Architect Rivals (Ace + Mega)
        if ArchitectRivalsDyad and "Ace" in roster and "Mega" in roster:
            self.dyads.append(ArchitectRivalsDyad())
            
        # 3. Signal Weavers (Janus + Quinn)
        if SignalWeaversDyad and "Janus" in roster and "Quinn" in roster:
            self.dyads.append(SignalWeaversDyad())
            
        # 4. Ceremonial Emergence (Oracle + Mico)
        if CeremonialEmergenceDyad and "Oracle" in roster and "Mico" in roster:
            self.dyads.append(CeremonialEmergenceDyad())

        # 5. Dynamic Sample Loading
        self._load_sample_dyads(roster)

    def _load_sample_dyads(self, roster: Dict[str, Agent]) -> None:
        """Dynamically load dyads from dyads/samples/"""
        samples_dir = Path(__file__).parent.parent / "dyads" / "samples"
        if not samples_dir.exists():
            return

        # Add to path temporarily to allow imports
        if str(samples_dir) not in sys.path:
            sys.path.append(str(samples_dir))

        for file_path in samples_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            module_name = file_path.stem
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Scan for classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and hasattr(attr, "check_requirements"):
                            # Check requirements
                            if attr.check_requirements(roster):
                                # Instantiate and add
                                try:
                                    self.dyads.append(attr())
                                    print(f"✨ Custom Dyad Loaded: {attr.__name__}")
                                except Exception as e:
                                    print(f"⚠️ Failed to instantiate {attr.__name__}: {e}")

            except Exception as e:
                print(f"⚠️ Failed to load sample dyad {module_name}: {e}")

    def on_turn_start(self, ctx: Any) -> List[Event]:
        events = []
        for dyad in self.dyads:
            events.extend(dyad.on_turn_start(ctx))
        return events

    def on_target_selected(self, ctx: Any, thrower_id: str, target_id: str) -> None:
        for dyad in self.dyads:
            dyad.on_target_selected(ctx, thrower_id, target_id)

    def on_hit(self, ctx: Any, thrower_id: str, target_id: str) -> List[Event]:
        events = []
        for dyad in self.dyads:
            events.extend(dyad.on_hit(ctx, thrower_id, target_id))
        return events

    def on_turn_end(self, ctx: Any) -> List[Event]:
        events = []
        for dyad in self.dyads:
            events.extend(dyad.on_turn_end(ctx))
        return events

    def check_interception(self, ctx: Any, thrower_id: str, target_id: str, rng: Any) -> Optional[str]:
        """
        Polls dyads to see if any interception occurs (e.g. Twin Rescue).
        Returns the new target ID if intercepted, else None.
        """
        for dyad in self.dyads:
            if hasattr(dyad, "check_interception"):
                new_target = dyad.check_interception(ctx, thrower_id, target_id, rng)
                if new_target:
                    return new_target
        return None
