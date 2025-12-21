import random
from typing import List, Tuple, Dict
from .models import Agent, Event

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def pick_target(rng: random.Random, thrower: Agent, agents: List[Agent], twin_rescue_target: str = None) -> Agent:
    """
    Selects a target.
    If twin_rescue_target is provided (pre-calculated interception), returns that agent.
    """
    if twin_rescue_target:
        # Resolve the name to an object
        rescuer = next((a for a in agents if a.name == twin_rescue_target), None)
        if rescuer:
            return rescuer

    options = [a for a in agents if a.name != thrower.name]
    return rng.choice(options)

def pick_ricochet_targets(
    rng: random.Random,
    agents: List[Agent],
    exclude_names: List[str],
    quinn_name: str = "Quinn",
    quinn_cap: float = 0.45,
    count: int = 1,
) -> List[Agent]:
    """
    Weighted pick, but cap Quinn's probability so he doesn't catch every stray.
    Returns up to `count` distinct targets.
    """
    candidates = [a for a in agents if a.name not in exclude_names]
    if not candidates:
        # Fallback if everyone else is excluded
        candidates = [a for a in agents if a.name != exclude_names[0]]

    picked: List[Agent] = []
    for _ in range(count):
        pool = [a for a in candidates if a.name not in {p.name for p in picked}]
        if not pool:
            break

        weights = []
        for a in pool:
            w = 1.0
            if a.name == quinn_name:
                w += a.stray_magnet
            weights.append(w)

        total = sum(weights)
        if total <= 0:
            picked.append(rng.choice(pool))
            continue

        # cap Quinn
        q_idx = next((i for i, a in enumerate(pool) if a.name == quinn_name), None)
        if q_idx is not None:
            q_prob = weights[q_idx] / total
            if q_prob > quinn_cap:
                wq = weights[q_idx]
                other = total - wq
                new_wq = (quinn_cap * other) / (1.0 - quinn_cap) if (1.0 - quinn_cap) > 0 else wq
                weights[q_idx] = max(0.01, new_wq)

        total = sum(weights)
        r = rng.random() * total
        acc = 0.0
        chosen = pool[-1]
        for a, w in zip(pool, weights):
            acc += w
            if r <= acc:
                chosen = a
                break
        picked.append(chosen)

    return picked

def ace_multiplier(ace: Agent) -> float:
    """
    Spite multiplier: 1.0 .. (1.0 + spite_max_bonus)
    """
    return ace.spite_min_multiplier + (ace.spite_meter * ace.spite_max_bonus)

def effective_dodge(agent: Agent) -> float:
    """
    Kryssie gets extra dodge while holding beer + abstaining.
    """
    if agent.name == "Kryssie" and agent.holding_beer:
        return clamp(agent.dodge + agent.beer_dodge_bonus)
    return agent.dodge

def apply_bankai_debuff(agent: Agent, intensity: float, resonance_debuff: float) -> float:
    """
    Reduces dodge chance based on Weaver intensity.
    """
    debuff = resonance_debuff * intensity
    return clamp(agent.dodge - debuff, 0.0, 0.92)

def compute_p_hit(roster: Dict[str, Agent], thrower: Agent, target: Agent, weaver_active: bool = False, weaver_intensity: float = 1.0, resonance_debuff: float = 0.0) -> float:
    # 1. Base Accuracy * Transient Mod
    acc = thrower.accuracy * thrower.accuracy_mod

    # Ace spite boosts Ace's throws based on meter (Legacy integration)
    if thrower.name == "Ace":
        acc *= ace_multiplier(roster["Ace"])

    # 2. Base Dodge * Transient Mod
    # We use effective_dodge logic but now we must account for the mod being separate? 
    # Or strict adherence: effective_dodge currently handles beer.
    # We should multiply the RESULT of effective_dodge by dodge_mod? 
    # OR apply mod to base first?
    # Mega-Warning: "If we multiply dodge *= 0.5... result is 0.0009" implies modification of properties.
    # But here we are computing p_hit.
    # Let's apply dodge_mod to the effective dodge capability.
    
    base_dod = effective_dodge(target)
    dod = base_dod * target.dodge_mod

    if weaver_active:
        # Bankai Debuff: Directly reduce effective dodge
        debuff = resonance_debuff * weaver_intensity
        dod = clamp(dod - debuff, 0.0, 0.92)

    p = acc * (1.0 - dod)
    return clamp(p)

def janus_untouchable_gate(janus: Agent, target: Agent) -> Tuple[bool, str]:
    if target.name != "Janus":
        return False, ""
    if janus.untouchable_while_budget and janus.paradox_budget > 0:
        janus.paradox_budget -= 1
        return True, f"Janus untouchable (budget now {janus.paradox_budget})."
    return False, ""

def maybe_janus_paradox_reroll(
    rng: random.Random,
    thrower: Agent,
    roll_hit: float
) -> Tuple[float, bool, str]:
    if thrower.name != "Janus":
        return roll_hit, False, ""
    if thrower.paradox_budget <= 0:
        return roll_hit, False, "Janus paradox budget exhausted."
    if rng.random() < thrower.paradox_chance:
        thrower.paradox_budget -= 1
        return rng.random(), True, f"Janus paradox reroll used (budget now {thrower.paradox_budget})."
    return roll_hit, False, ""

def apply_turn_decay(roster: Dict[str, Agent]) -> None:
    # Ace spite meter decays every turn
    if "Ace" in roster:
        ace = roster["Ace"]
        ace.spite_meter = clamp(ace.spite_meter - ace.spite_decay_per_turn)
