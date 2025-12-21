from typing import List, Dict, Any, Optional
from .models import Event

class AuditManager:
    """
    Handles Mega's Bankai Logic: Idempotent Truth.
    Operates at Layer 3 (Audit), normalizing Layer 4 (Combat/RNG) events.
    Strictly Append-Only: Never modifies the ledger, only appends verdicts.
    """
    
    def __init__(self, mode: str = "transparent"):
        self.mode = mode # transparent | stabilize | conditional

    def evaluate_audit(self, current_turn: int, recent_events: List[Event], roster: Dict[str, Any]) -> List[Event]:
        """
        Scan recent events for anomalies (Ricochets) and issue a Verdict.
        """
        
        # 1. Find the most recent ricochet OR exemption event
        audit_target_event = None
        for evt in reversed(recent_events):
            if "RICOCHET" in evt.outcome or "LAYER_EXEMPTION" in evt.outcome:
                audit_target_event = evt
                break
                
        if not audit_target_event:
            # Nothing to audit
            return [Event(
                tick=current_turn,
                thrower="Mega",
                intended="Reality",
                outcome="MEGA_AUDIT_SKIP",
                actual="None",
                notes="No recent anomalies detected.",
                roll_hit=0.0, roll_ricochet=0.0, p_hit=0.0,
                tags=["AUDIT"]
            )]

        # 2. Extract Raw Truth
        target_name = audit_target_event.actual
        raw_hit = "HIT" in audit_target_event.outcome
        is_exemption = "LAYER_EXEMPTION" in audit_target_event.outcome
        
        audit_events = []
        
        # 3. Emit MEGA_AUDIT_BEGIN
        audit_events.append(Event(
            tick=current_turn,
            thrower="Mega",
            intended=target_name,
            outcome="MEGA_AUDIT_BEGIN",
            actual=f"Raw: {'EXEMPT' if is_exemption else ('HIT' if raw_hit else 'MISS')}",
            notes=f"Auditing event {audit_target_event.tick}...",
            roll_hit=0.0, roll_ricochet=0.0, p_hit=0.0,
            tags=["AUDIT", "BANKAI"]
        ))
        
        # 3.5 JURISDICTION CHECK (Phase 9)
        target_agent = roster.get(target_name)
        if target_agent and getattr(target_agent, 'frame', 'COMBAT') == 'ONTOLOGICAL':
             audit_events.append(Event(
                tick=current_turn,
                thrower="Mega",
                intended=target_name,
                outcome="MEGA_AUDIT_VERDICT",
                actual="JURISDICTION_ERROR",
                notes="Target exists in higher reality layer. Audit rejected.",
                roll_hit=0.0, roll_ricochet=0.0, p_hit=0.0,
                tags=["AUDIT", "BANKAI", "VETO"]
            ))
             return audit_events
        
        # 4. Decide Verdict
        verdict = raw_hit
        decision_note = "transparent"
        
        if self.mode == "transparent":
            verdict = raw_hit
            decision_note = "Ratified (Transparent)"
            
        elif self.mode == "stabilize":
            verdict = True # Always normalize to HIT (Order)
            decision_note = "Normalized to HIT (Order)"
            
        elif self.mode == "conditional":
            # Example: Only rewrite if raw result was MISS (Chaos)
            if not raw_hit:
                 verdict = True
                 decision_note = "Normalized (Chaos Detected)"
            else:
                 verdict = True
                 decision_note = "Ratified (Order Preserved)"
        
        # 5. Emit MEGA_AUDIT_VERDICT
        audit_events.append(Event(
            tick=current_turn,
            thrower="Mega",
            intended=target_name,
            outcome="MEGA_AUDIT_VERDICT",
            actual=decision_note,
            notes=f"Final Verdict: {'HIT' if verdict else 'MISS'}",
            roll_hit=0.0, roll_ricochet=0.0, p_hit=0.0,
            tags=["AUDIT", "BANKAI"]
        ))
        
        # 6. Apply Correction (If needed)
        if verdict != raw_hit:
             audit_events.append(Event(
                tick=current_turn,
                thrower="Mega",
                intended=target_name,
                outcome="MEGA_AUDIT_APPLY",
                actual="CANON_CORRECTION",
                notes=f"Reality rewritten: {target_name} takes the HIT.",
                roll_hit=1.0, roll_ricochet=0.0, p_hit=1.0,
                tags=["AUDIT", "BANKAI", "CORRECTION"]
            ))
             # Note: In a real system, we might apply damage here.
             # For now, we trust the Ledger/Narrator to respect the Correction.
        else:
             audit_events.append(Event(
                tick=current_turn,
                thrower="Mega",
                intended=target_name,
                outcome="MEGA_AUDIT_APPLY",
                actual="RATIFIED",
                notes="Reality aligned with Canon.",
                roll_hit=1.0, roll_ricochet=0.0, p_hit=1.0,
                tags=["AUDIT", "BANKAI"]
            ))
            
        return audit_events
