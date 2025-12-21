from typing import List, Dict, Any, Optional

class ScenarioQueue:
    """
    Holds a list of forced actions that are executed on a specific turn.
    Used for testing specific systemic interactions (e.g. Ricochet Audit).
    
    Actions are "intents" - they drive agent behavior but resolve through 
    standard physics engines unless explicitly overriding via Bankai.
    """
    def __init__(self):
        self.name: Optional[str] = None
        self.actions: List[Dict[str, Any]] = []

    def load(self, name: str) -> None:
        """Load a hard-coded scenario by name"""
        self.name = name
        self.actions = []
        
        if name == "ricochet_audit":
            # --- THE RICOCHET AUDIT SCENARIO ---
            # Goal: Test if Mega's Bankai can "stabilize" a stochastic Ricochet into Canon.
            
            # Turn 1: Ace Activates Bankai (Deterministic Strategy)
            self.actions.append({
                "turn": 1, 
                "actor": "Ace", 
                "intent": "BANKAI_RELEASE", 
                "target": None
            })
            
            # Turn 2: Forced Ricochet (Stochastic Event)
            # The simulator will force the resolver to choose a ricochet path,
            # but the hit/miss is still RNG (unless we cheat, but we won't).
            self.actions.append({
                "turn": 2, 
                "actor": "Any", # Simulator chooses thrower
                "intent": "FORCE_RICOCHET", 
                "target": None # Will use CLI arg or default
            })
            
            # Turn 3: Mega Audits the Result (Idempotent Truth)
            self.actions.append({
                "turn": 3, 
                "actor": "Mega", 
                "intent": "MEGA_AUDIT", 
                "target": None
            })
            
            # Turn 4: Kryssie observes from Ontological Layer
            self.actions.append({
                "turn": 4, 
                "actor": "Kryssie", 
                "intent": "BEER_SIP", 
                "target": None
            })
            
        elif name == "hierarchy_test":
            # --- THE HIERARCHY CHALLENGE ---
            # Goal: Prove Layer 0 (Ontology) overrides Layer 3 (Audit).
            
            # Turn 1: Kryssie enters Beer Mode (Ontological)
            self.actions.append({
                "turn": 1, "actor": "Kryssie", "intent": "BEER_SIP", "target": None
            })
            
            # Turn 2: Force Ricochet -> Kryssie
            # We want the *intent* to be a hit on Kryssie, via Ricochet
            # MUST NOT be Kryssie acting, or she will just Sip Beer.
            self.actions.append({
                "turn": 2, "actor": "Ace", "intent": "FORCE_RICOCHET_ON_ONTOLOGICAL", "target": "Kryssie"
            })
            
            # Turn 3: Mega attempts to Audit the "Miss" (or "Exemption")
            self.actions.append({
                "turn": 3, "actor": "Mega", "intent": "MEGA_AUDIT", "target": None
            })
            
        else:
            print(f"⚠️ Unknown scenario: {name}")

    def get_actions_for_turn(self, turn: int) -> List[Dict[str, Any]]:
        """Retrieve all forced actions for a given turn"""
        return [a for a in self.actions if a["turn"] == turn]
