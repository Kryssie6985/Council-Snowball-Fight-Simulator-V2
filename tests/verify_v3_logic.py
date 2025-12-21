
import sys
import os
from pathlib import Path
from dataclasses import dataclass

# Add root to path so we can import core/dyads
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dyads.signal_weavers import SignalWeaversDyad
from core.models import Event, Agent

# Mock Context
@dataclass
class MockContext:
    roster: dict
    tick: int

def verify_v3_logic():
    print("🧪 Verifying Signal Weavers V3 Logic...")
    
    # 1. Setup Agents
    janus = Agent(name="Janus", paradox_budget=0) # START EMPTY to trigger lock
    quinn = Agent(name="Quinn")
    roster = {"Janus": janus, "Quinn": quinn}
    ctx = MockContext(roster=roster, tick=1)
    
    dyad = SignalWeaversDyad()
    
    # 2. Trigger Lock (Janus Empty -> Turn Start)
    print("\n[Step 1] Triggering Pattern Lock (Janus Budget = 0)...")
    events = dyad.on_turn_start(ctx)
    lock_event = next((e for e in events if e.outcome == "PATTERN_LOCK"), None)
    
    if lock_event:
        print(f"✅ LOCK ACTIVATED: {lock_event.notes}")
        print(f"   State: lock_active={dyad.state.lock_active}")
    else:
        print("❌ FAILED to trigger Pattern Lock.")
        return

    # 3. Trigger Cycle Renewal (Janus Hits during Lock)
    print("\n[Step 2] Janus Hits Quinn (Active Reload)...")
    # Janus hits Quinn
    hit_events = dyad.on_hit(ctx, thrower_id="Janus", target_id="Quinn")
    
    cycle_event = next((e for e in hit_events if e.outcome == "CYCLE_RENEWAL"), None)
    
    if cycle_event:
        print(f"✅ CYCLE RENEWAL DETECTED: {cycle_event.notes}")
        print(f"   Janus Budget: {janus.paradox_budget} (Expected > 0)")
        print(f"   Lock Active: {dyad.state.lock_active} (Expected False)")
        
        if janus.paradox_budget > 0 and not dyad.state.lock_active:
             print("✨ SUCCESS: Logic is sound. Cycle renewed.")
        else:
             print("⚠️  PARTIAL SUCCESS: Event fired but state mismatch.")
    else:
        print("❌ FAILED to trigger Cycle Renewal.")
        print("   Events returned:", [e.outcome for e in hit_events])

if __name__ == "__main__":
    verify_v3_logic()
