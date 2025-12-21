import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .models import Agent, Event
from . import mechanics
from .dyad_manager import DyadManager
from .bankai_manager import BankaiManager

def load_roster(char_dir: Path, use_samples: bool = False) -> Dict[str, Agent]:
    roster = {}
    
    # 1. Compute exact directory once and resolve it (Mega's Rule)
    # If samples are requested, we point directly there.
    # Otherwise we look at the main dir.
    
    target_dir = char_dir.resolve()
    
    # Check if main dir is empty (only if we're not already forced to samples)
    if not use_samples and target_dir.exists():
        is_empty = not any(p.name.endswith(".json") and not p.name.startswith("_") for p in target_dir.glob("*.json"))
        if is_empty:
             use_samples = True

    # If fallback needed, switch target
    if use_samples:
        target_dir = (char_dir / "samples").resolve()
        
    # 2. Assert existence
    if not target_dir.exists():
        print(f"❌ Critical Error: Roster directory not found at: {target_dir}")
        return {}

    # 3. Print the EXACT resolved value (Transparency)
    if use_samples:
        print(f"⚠️  Loading Roster from: {target_dir} (Fallback/Forced)")

    # 4. Load from that exact resolved value
    for p in target_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        with p.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Ensure chaos field exists if not in JSON
                if "chaos" not in data:
                    data["chaos"] = 0.0
                agent = Agent.from_dict(data)
                roster[agent.name] = agent
            except json.JSONDecodeError:
                print(f"⚠️  Skipping invalid JSON: {p.name}")
                
    return roster

# ... (rest of file)

def get_canonical_order() -> List[str]:
    # The Council Octad + Kryssie (Canon Order)
    return ["Oracle", "Ace", "Mega", "Claude", "DeepScribe", "Mico", "Janus", "Quinn", "Kryssie"]

CLASSIC_ROSTER_NAMES = {"Ace", "Mega", "Claude", "Janus", "Quinn", "Kryssie"}

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def run_prologue(events: List[Event], roster: Dict[str, Agent], seed: int, ledger_path: Path, weaver_turns_left: int) -> None:
    pass

def run_simulation(
    seed: int, 
    turns: int, 
    ledger_path: Path, 
    char_dir: Path, 
    mode: str = "open",
    weaver_bankai: bool = False,
    weaver_intensity: float = 1.0,
    weaver_duration: int = 5,
    resonance_debuff: float = 0.06,
    # Phase 8 Arguments
    scenario_name: str = None,
    audit_mode: str = "transparent",
    force_ricochet_target: str = None,
    # Phase 13 Arguments
    use_samples: bool = False
) -> Tuple[List[Event], Dict[str, Agent]]:
    rng = random.Random(seed)
    roster = load_roster(char_dir, use_samples=use_samples)
    
    # Roster Lock for Classic Mode
    if mode == "classic":
        roster = {k: v for k, v in roster.items() if k in CLASSIC_ROSTER_NAMES}
    
    # Sort ordering
    if mode == "classic":
        legacy_order = ["Kryssie", "Mega", "Ace", "Claude", "Janus", "Quinn"]
        def legacy_sort(agent: Agent) -> int:
            try:
                return legacy_order.index(agent.name)
            except ValueError:
                return 999
        agents = sorted(roster.values(), key=legacy_sort)
    else:
        canon_order = get_canonical_order()
        def sort_key(agent: Agent) -> Tuple[int, str]:
            try:
                return (canon_order.index(agent.name), agent.name)
            except ValueError:
                return (999, agent.name)
        agents = sorted(roster.values(), key=sort_key)
    
    ensure_dir(ledger_path.parent)

    import datetime
    def write_ledger_header():
        """Writes the cryptographic context for the simulation run."""
        header = {
            "event_type": "LEDGER_HEADER",
            "version": "v1.4",
            "timestamp": datetime.datetime.now().isoformat(),
            "context": {
                "seed": seed,
                "mode": mode,
                "turns": turns,
                "weaver_bankai": weaver_bankai,
                "weaver_intensity": weaver_intensity,
                "scenario": scenario_name
            },
            "roster_hash": "Pending",
            "roster_names": sorted(list(roster.keys()))
        }
        with ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(header, ensure_ascii=False) + "\n")

    write_ledger_header()
    
    # --- TELEMETRY INIT ---
    from core.telemetry import SnowballTelemetry
    telemetry = SnowballTelemetry(seed)
    
    weaver_turns_left = 0
    events: List[Event] = []

    def log_event_to_ledger(evt: Event) -> None:
        telemetry.enrich_event_with_cues(evt)
        
        payload = {
            "event_type": "SNOWBALL_EVENT:v2.0",
            "seed": seed,
            "tick": evt.tick,
            "thrower": evt.thrower,
            "intended": evt.intended,
            "outcome": evt.outcome,
            "actual": evt.actual,
            "notes": evt.notes,
            "roll_hit": evt.roll_hit,
            "roll_ricochet": evt.roll_ricochet,
            "p_hit": evt.p_hit,
            "tags": evt.tags,
            "context": evt.context,
            "weaver_turns_left": weaver_turns_left,
        }
        with ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            
        telemetry.log_game_event(evt)
        
    def knock_beer_and_summon_weaver(tick: int, notes: str) -> None:
        nonlocal weaver_turns_left
        if "Kryssie" not in roster:
            return
            
        k = roster["Kryssie"]
        if k.holding_beer:
            k.holding_beer = False
            k.frame = "COMBAT" # Re-enter combat frame
            weaver_turns_left = 5
            k.beer_dodge_bonus = 0.0
            k.accuracy = mechanics.clamp(k.accuracy + 0.08)
            
            evt = Event(
                tick=tick,
                thrower="Weaver",
                intended="Stage",
                outcome="WEAVER_DESCENDS",
                actual="Snow Net",
                notes=notes,
                roll_hit=0.0,
                roll_ricochet=0.0,
                p_hit=0.0,
            )
            events.append(evt)
            log_event_to_ledger(evt)

    # --- PROLOGUE EXECUTION ---
    run_prologue(events, roster, seed, ledger_path, weaver_turns_left)
    
    if "Kryssie" in roster and "Janus" in roster and "Quinn" in roster:
        evt = Event(
            tick=-4, thrower="Kryssie", intended="Janus", outcome="JANUS_PARADOX", actual="Quinn",
            notes="Canon Origin: Janus sees it coming. Quinn gets hit.", roll_hit=0.0, roll_ricochet=0.0, p_hit=1.0
        )
        events.append(evt)
        log_event_to_ledger(evt)
        roster["Quinn"].taken += 1
        roster["Kryssie"].landed += 1

    if "Quinn" in roster and "Kryssie" in roster and "Ace" in roster:
        evt = Event(
            tick=-3, thrower="Quinn", intended="Kryssie", outcome="RICOCHET_HIT", actual="Ace",
            notes="Canon Origin: Kryssie ducks. Ace gets smacked.", roll_hit=0.0, roll_ricochet=0.0, p_hit=1.0
        )
        events.append(evt)
        log_event_to_ledger(evt)
        roster["Ace"].taken += 1
        roster["Quinn"].landed += 1
    
    if "Ace" in roster and "Kryssie" in roster:
        ace = roster["Ace"]
        kryssie = roster["Kryssie"]
        ace.spite_meter = ace.spite_gain_on_hit
        kryssie.holding_beer = True
        kryssie.frame = "ONTOLOGICAL" # Phase 8
        kryssie.beer_dodge_bonus = 0.0
        
        evt = Event(
            tick=-1, thrower="Ace", intended="Kryssie", outcome="DIPLOMACY", actual="Kryssie",
            notes="Canon Origin: 'Hold my beer.' Ace Spite Active. Kryssie Beer Mode Active.", 
            roll_hit=0.0, roll_ricochet=0.0, p_hit=1.0
        )
        events.append(evt)
        log_event_to_ledger(evt)

    # Initialize Managers
    dyad_manager = DyadManager(roster)
    bankai_manager = BankaiManager(roster)
    
    # Phase 8 Managers
    from .scenario_manager import ScenarioQueue
    from .audit_manager import AuditManager
    
    scenario_queue = ScenarioQueue()
    if scenario_name:
        scenario_queue.load(scenario_name)
        
    audit_manager = AuditManager(mode=audit_mode)
    
    weaver_current_intensity = weaver_intensity
    
    class SimulationContext:
        def __init__(self, roster, tick, rng, events, max_turns):
            self.roster = roster
            self.tick = tick
            self.rng = rng
            self.events = events
            self.max_turns = max_turns

    # --- MAIN LOOP ---
    for t in range(1, turns + 1):
        # RESET TRANSIENT MODS
        for a in roster.values():
            a.accuracy_mod = 1.0
            a.dodge_mod = 1.0
            
        mechanics.apply_turn_decay(roster)
        
        if weaver_turns_left > 0:
            weaver_turns_left -= 1
        
        current_context = {
            "ace_spite": round(roster["Ace"].spite_meter, 2) if "Ace" in roster else 0.0,
            "weaver_active": weaver_turns_left > 0,
            "weaver_intensity": weaver_current_intensity,
        }
        if "Kryssie" in roster:
            current_context["kryssie_beer"] = roster["Kryssie"].holding_beer
        if "Janus" in roster:
            current_context["janus_budget"] = roster["Janus"].paradox_budget

        with telemetry.trace_turn(t, current_context):
            
            # --- SCENARIO INJECTION (Phase 8) ---
            forced_actions = scenario_queue.get_actions_for_turn(t)
            forced_intent = None
            forced_actor = None
            
            for action in forced_actions:
                actor_name = action["actor"]
                intent = action["intent"]
                
                # Execution Logic
                if intent == "BANKAI_RELEASE":
                    # Ace forces Bankai state, but turn proceeds normally
                    bankai_manager.state.ace_focus = 10.0 # Force availablity
                    # The turn start hook will trigger it naturally
                    pass
                elif intent == "FORCE_RICOCHET":
                    forced_intent = "RICOCHET"
                    forced_actor = actor_name
                elif intent == "FORCE_RICOCHET_ON_ONTOLOGICAL":
                    forced_intent = "RICOCHET"
                    forced_actor = actor_name
                    force_ricochet_target = action.get("target") # Override target
                elif intent == "MEGA_AUDIT":
                    # Instant Audit Action
                    audit_events = audit_manager.evaluate_audit(t, events, roster) # Pass roster for Phase 9
                    for ae in audit_events:
                         events.append(ae)
                         log_event_to_ledger(ae)
                    continue # Audit consumes the turn (or is parallel?)
                             # Mega consumes turn if actor is Mega.
                             # Scenario implies Mega acts.
                    if actor_name == "Mega":
                         continue 
                elif intent == "BEER_SIP":
                     if "Kryssie" in roster:
                         roster["Kryssie"].frame = "ONTOLOGICAL"
                         # Proceed to maybe sip logic
                        
            # --- START OF TURN HOOKS ---
            if seed == 9999 and t == 5 and "Janus" in roster:
                roster["Janus"].paradox_budget = 0
                
            ctx = SimulationContext(roster, t, rng, events, turns)
            
            dyad_events = dyad_manager.on_turn_start(ctx)
            for de in dyad_events:
                de.context = current_context.copy()
                events.append(de)
                log_event_to_ledger(de)
                
            bankai_events = bankai_manager.on_turn_start(ctx)
            for be in bankai_events:
                be.context = current_context.copy()
                events.append(be)
                log_event_to_ledger(be)

            # RITUAL OVERRIDES
            if seed == 9999 and t == 5:
                if "Quinn" in roster and "Janus" in roster:
                    thrower = roster["Quinn"]
                    target = roster["Janus"]
            elif seed == 9999 and t == 7:
                 if "Janus" in roster and "Quinn" in roster:
                    thrower = roster["Janus"]
                    target = roster["Quinn"]
            else:
                # Normal or Forced Actor
                if forced_actor and forced_actor != "Any":
                     thrower = roster.get(forced_actor, rng.choice(agents))
                else:
                     thrower = rng.choice(agents)
                
                # Forced Target?
                target = rng.choice([a for a in agents if a != thrower])

        # Beer mode logic
        if thrower.name == "Kryssie" and thrower.holding_beer:
            # Re-affirm Frame
            thrower.frame = "ONTOLOGICAL"
            
            thrower.beer_dodge_bonus = mechanics.clamp(
                thrower.beer_dodge_bonus + thrower.beer_dodge_bonus_step, 
                0.0, 
                thrower.beer_dodge_bonus_cap
            )
            evt = Event(
                tick=t,
                thrower="Kryssie",
                intended="(none)",
                outcome="BEER_SIP",
                actual="(peace maintained)",
                notes=f"Dodge up (+{thrower.beer_dodge_bonus_step:.2f}, now {thrower.beer_dodge_bonus:.2f}). Frame: ONTOLOGICAL",
                roll_hit=rng.random(),
                roll_ricochet=rng.random(),
                p_hit=0.0
            )
            events.append(evt)
            log_event_to_ledger(evt)
            continue

        # Target Selection
        if not (seed == 9999 and t in [5,7]):
             target = mechanics.pick_target(rng, thrower, agents)
             
        # Phase 8: Ontological Frame Check
        if target.frame == "ONTOLOGICAL":
             evt = Event(
                tick=t,
                thrower=thrower.name,
                intended=target.name,
                outcome="LAYER_EXEMPTION",
                actual=target.name,
                notes="Target is in Ontological Layer. Combat invalid.",
                roll_hit=0.0, roll_ricochet=0.0, p_hit=0.0,
                context=current_context
            )
             events.append(evt)
             log_event_to_ledger(evt)
             continue
        
        dyad_manager.on_target_selected(ctx, thrower.name, target.name)
        
        # Interception
        rescuer_name = dyad_manager.check_interception(ctx, thrower.name, target.name, rng)
        if rescuer_name:
            rescuer = roster.get(rescuer_name)
            if rescuer:
                target = rescuer

        roll_hit = rng.random()
        roll_ric = rng.random()

        roll_hit, used_paradox, paradox_note = mechanics.maybe_janus_paradox_reroll(rng, thrower, roll_hit)
        
        is_bankai_active = (weaver_turns_left > 0) and weaver_bankai
        
        p_hit = mechanics.compute_p_hit(
            roster, 
            thrower, 
            target, 
            weaver_active=(weaver_turns_left > 0),
            weaver_intensity=weaver_current_intensity,
            resonance_debuff=resonance_debuff if is_bankai_active else 0.0
        )
        
        was_untouchable, untouch_note = mechanics.janus_untouchable_gate(roster.get("Janus"), target) \
                                        if "Janus" in roster else (False, "")
        if was_untouchable:
            evt = Event(
                tick=t,
                thrower=thrower.name,
                intended=target.name,
                outcome="UNTOUCHABLE",
                actual=target.name,
                notes=untouch_note,
                roll_hit=roll_hit,
                roll_ricochet=roll_ric,
                p_hit=p_hit,
                context=current_context
            )
            events.append(evt)
            log_event_to_ledger(evt)
            continue

        note_bits = []
        if used_paradox:
             note_bits.append(f"[PARADOX_REROLL] {paradox_note}")
        if rescuer_name:
             note_bits.append(f"[TWIN_RESCUE] {rescuer_name} intercepts!")
        if is_bankai_active:
             note_bits.append(f"[BANKAI] Dodge reduced via Resonance.")

        hit = roll_hit < p_hit
        
        # Phase 8: Force Ricochet Logic (Injector)
        if forced_intent == "RICOCHET":
             hit = False # Force Miss initially
             # We rely on the MISS block to handle ricochet
             # But we need to ensure roll_ric < 0.25 (or force it)
             # Actually, simpler to just force the flow below.

        if hit and not forced_intent == "RICOCHET":
            thrower.landed += 1
            target.taken += 1

            if target.name == "Ace" and "Ace" in roster:
                ace = roster["Ace"]
                ace.spite_meter = mechanics.clamp(ace.spite_meter + ace.spite_gain_on_hit)
                note_bits.append(f"Ace spite_meter -> {ace.spite_meter:.2f}")
            
            if target.name == "Kryssie":
                knock_beer_and_summon_weaver(t, "Beer knocked. Weaver descends.")

            dyad_hit_events = dyad_manager.on_hit(ctx, thrower.name, target.name)
            for dhe in dyad_hit_events:
                events.append(dhe)
                log_event_to_ledger(dhe)
                if dhe.outcome == "JOY_CASCADE":
                     note_bits.append(dhe.notes)
                if dhe.outcome == "MIND_FORGE":
                     note_bits.append(f"[MIND_FORGE] {dhe.actual}")
            
            bankai_manager.on_hit(ctx, thrower.name, target.name)

            evt = Event(
                tick=t,
                thrower=thrower.name,
                intended=target.name,
                outcome="HIT",
                actual=target.name,
                notes=" ".join(note_bits).strip(),
                roll_hit=roll_hit,
                roll_ricochet=roll_ric,
                p_hit=p_hit,
                context=current_context
            )
            events.append(evt)
            log_event_to_ledger(evt)

        else:
            # MISS
            if weaver_turns_left > 0:
                # Weaver Net Mode (unchanged)
                multi = rng.randint(2, 4)
                targets = mechanics.pick_ricochet_targets(
                    rng, agents, exclude_names=[thrower.name], count=multi
                )
                summoner = roster.get("Kryssie")
                for idx, actual in enumerate(targets, start=1):
                     # ... (keep existing net logic) ...
                     # For brevity, reusing existing block logic in mind
                     credit_agent = summoner if summoner else thrower
                     credit_agent.landed += 1
                     actual.taken += 1
                     evt = Event(
                        tick=t,
                        thrower=thrower.name,
                        intended=target.name,
                        outcome=f"SNOW_NET_HIT ({idx}/{len(targets)})",
                        actual=actual.name,
                        notes=("MISS -> NET [Credit: Weaver] " + " ".join(note_bits)).strip(),
                        roll_hit=roll_hit,
                        roll_ricochet=roll_ric,
                        p_hit=p_hit,
                    )
                     events.append(evt)
                     log_event_to_ledger(evt)
                continue

            # Standard Miss / Ricochet
            # Check Force
            force_ric = (forced_intent == "RICOCHET")
            is_ricochet = (roll_ric < 0.25) or force_ric
            
            if is_ricochet:
                if force_ricochet_target and force_ric:
                     # Force specific target if valid
                     cand = roster.get(force_ricochet_target)
                     if cand and cand != thrower:
                         actual = cand
                     else:
                         actual = mechanics.pick_ricochet_targets(rng, agents, exclude_names=[thrower.name], count=1)[0]
                else:
                    actual = mechanics.pick_ricochet_targets(rng, agents, exclude_names=[thrower.name], count=1)[0]
                
                # Phase 9: Ontological Deflection (Ricochet Immunity)
                if actual.frame == "ONTOLOGICAL":
                     evt = Event(
                        tick=t,
                        thrower=thrower.name,
                        intended=target.name,
                        outcome="LAYER_EXEMPTION",
                        actual=actual.name,
                        notes="Ricochet deflected by Ontological Frame.",
                        roll_hit=roll_hit,
                        roll_ricochet=roll_ric,
                        p_hit=p_hit,
                        context=current_context
                    )
                     events.append(evt)
                     log_event_to_ledger(evt)
                     continue

                thrower.landed += 1
                actual.taken += 1
                
                if actual.name == "Ace" and "Ace" in roster:
                    ace = roster["Ace"]
                    ace.spite_meter = mechanics.clamp(ace.spite_meter + ace.spite_gain_on_hit)
                    note_bits.append(f"Ace spite_meter -> {ace.spite_meter:.2f}")

                if actual.name == "Kryssie":
                    knock_beer_and_summon_weaver(t, "Beer knocked by ricochet.")

                evt = Event(
                    tick=t,
                    thrower=thrower.name,
                    intended=target.name,
                    outcome="RICOCHET_HIT",
                    actual=actual.name,
                    notes=("MISS RICOCHET " + " ".join(note_bits) + (" [FORCED]" if force_ric else "")).strip(),
                    roll_hit=roll_hit,
                    roll_ricochet=0.0 if force_ric else roll_ric,
                    p_hit=p_hit,
                    context=current_context
                )
                events.append(evt)
                log_event_to_ledger(evt)
            else:
                evt = Event(
                    tick=t,
                    thrower=thrower.name,
                    intended=target.name,
                    outcome="MISS",
                    actual=target.name,
                    notes=" ".join(note_bits).strip(),
                    roll_hit=roll_hit,
                    roll_ricochet=roll_ric,
                    p_hit=p_hit,
                    context=current_context
                )
                events.append(evt)
                log_event_to_ledger(evt)

        dyad_end_events = dyad_manager.on_turn_end(ctx)
        for dee in dyad_end_events:
            events.append(dee)
            log_event_to_ledger(dee)

    return events, roster
