
import argparse
import sys
import shutil
from pathlib import Path

# Ensure core imports work
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core.simulation import run_simulation
from core.mechanics import ace_multiplier
from core.models import Event
from core.auto_narrative_generator import LedgerParser, PatternDetector, StoryGenerator

# --- UTILS ---

def print_timeline(events: list[Event], limit: int = 0) -> None:
    for evt in events[:limit] if limit else events:
        note = f" :: {evt.notes}" if evt.notes else ""
        print(f"[t{evt.tick:02d}] {evt.thrower} ➜ {evt.intended} :: {evt.outcome} -> {evt.actual}{note}")

def print_scoreboard(roster: dict) -> None:
    rows = sorted(roster.values(), key=lambda a: (a.landed, -a.taken), reverse=True)
    print("\n--- SCOREBOARD ---")
    for a in rows:
        extra = ""
        if a.name == "Janus":
            extra = f" | paradox_budget={a.paradox_budget}"
        if a.name == "Ace":
            mult = ace_multiplier(a)
            extra = f" | spite_meter={a.spite_meter:.2f} | mult={mult:.2f}x"
        if a.name == "Kryssie":
            extra = f" | beer={a.holding_beer} | beer_dodge_bonus={a.beer_dodge_bonus:.2f}"
        print(f"{a.name:7s}  landed: {a.landed:2d} | taken: {a.taken:2d}{extra}")

def run_session(args, ledger_path: Path):
    char_dir = current_dir / "characters"
    
    # Clear ledger
    ledger_path.write_text("", encoding="utf-8")

    print(f"❄️  Snowball Session: Mode={args.mode}, Seed={args.seed}, Turns={args.turns}")
    
    scenario = getattr(args, 'scenario', None)
    audit_mode = getattr(args, 'audit_mode', 'transparent')
    force_target = getattr(args, 'force_ricochet_target', None)
    use_samples = getattr(args, 'samples', False)
    
    events, roster = run_simulation(
        seed=args.seed, 
        turns=args.turns, 
        ledger_path=ledger_path, 
        char_dir=char_dir, 
        mode=args.mode,
        weaver_bankai=True, # Default to True in CLI
        weaver_intensity=1.0,
        scenario_name=scenario,
        audit_mode=audit_mode,
        force_ricochet_target=force_target,
        use_samples=use_samples
    )

    if getattr(args, 'generate_story', False):
        print("\n💜 invoking Narrative Engine...")
        parser_engine = LedgerParser(ledger_path)
        evts, chars = parser_engine.parse()
        detector = PatternDetector(evts, chars)
        patterns = detector.detect()
        generator = StoryGenerator(evts, chars, patterns, args.seed)
        story = generator.generate()
        
        out_path = Path(getattr(args, 'story_out', 'story.md'))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(story, encoding='utf-8')
        print(f"✨ Story Generated: {out_path}")

    # Output
    timeline_limit = getattr(args, 'timeline', 0)
    print_timeline(events, limit=timeline_limit)
    print_scoreboard(roster)
    
    # Portfolio Summary JSON (Mega's Flex)
    summary_mode = getattr(args, 'summary', None)
    if summary_mode == 'json':
        import json
        hit_count = sum(1 for e in events if e.outcome in ["HIT", "RICOCHET_HIT", "SNOW_NET_HIT"])
        miss_count = sum(1 for e in events if e.outcome in ["MISS", "RICOCHET_MISS", "DODGE"])
        ricochet_count = sum(1 for e in events if "RICOCHET" in e.outcome)
        
        # Find MVP
        top_scorer = max(roster.values(), key=lambda a: a.landed) if roster else None
        
        summary_data = {
            "seed": args.seed,
            "turns": args.turns,
            "source": "samples" if use_samples else "custom",
            "counts": {
                "HIT": hit_count,
                "MISS": miss_count,
                "RICOCHET": ricochet_count
            },
            "mvp": {
                 "name": top_scorer.name if top_scorer else "None",
                 "score": top_scorer.landed if top_scorer else 0
            }
        }
        print("\n--- SUMMARY JSON ---")
        print(json.dumps(summary_data, indent=2))

# --- COMMANDS ---

def command_play(args):
    """Standard Play Mode"""
    ledger = Path("skeletor_ledger/snowball_events.jsonl")
    run_session(args, ledger)

def command_verify(args):
    """Verification Suite"""
    ledger = Path("skeletor_ledger/snowball_events.jsonl")
    
    if args.target == "all":
        targets = ["chaos", "lock", "audit", "hierarchy"]
    else:
        targets = [args.target]

    for t in targets:
        print(f"\n🧪 RUNNING VERIFICATION: {t.upper()}")
        print("="*40)
        
        # Setup specific args dynamically
        if t == "chaos":
            args.seed = 777
            args.turns = 20
            args.scenario = None
            args.generate_story = True
            args.story_out = "reports/verify_chaos_777.md"
        elif t == "lock":
            args.seed = 888
            args.turns = 20
            args.scenario = None
            args.generate_story = True
            args.story_out = "reports/verify_lock_888.md"
        elif t == "audit":
            args.seed = 1002
            args.turns = 10
            args.scenario = "ricochet_audit"
            args.audit_mode = "stabilize"
            args.generate_story = True
            args.story_out = "reports/verify_audit_1002.md"
        elif t == "hierarchy":
            args.seed = 1003
            args.turns = 5
            args.scenario = "hierarchy_test"
            args.audit_mode = "stabilize"
            args.generate_story = True
            args.story_out = "reports/verify_hierarchy_1003.md"
            
        run_session(args, ledger)
        print("✅ Verified.")

def command_chronicle(args):
    """Season 1 Compilation"""
    print("📚 compiling Season 1 Chronicle...")
    
    seeds = [
        (777, "The Chaos Fall"),
        (888, "The Pattern Lock"),
        (1001, "The Bankai Awakening"),
        (1002, "The Audit"),
        (1003, "The Hierarchy")
    ]
    
    ledger = Path("skeletor_ledger/snowball_events.jsonl")
    full_chronicle = ["# ❄️ THE COUNCIL CHRONICLE: SEASON 1 ❄️\n\n"]
    
    for seed, title in seeds:
        print(f"   > Processing {title} (Seed {seed})")
        # Configure run
        args.seed = seed
        args.turns = 15 # Standardize
        
        # Special configs per seed
        if seed == 1002: 
            args.scenario = "ricochet_audit"
            args.audit_mode = "stabilize"
        elif seed == 1003:
            args.scenario = "hierarchy_test"
            args.audit_mode = "stabilize"
            args.turns = 5
        else:
            args.scenario = None
            
        run_session(args, ledger)
        
        # Generate Narrative
        parser_engine = LedgerParser(ledger)
        evts, chars = parser_engine.parse()
        detector = PatternDetector(evts, chars)
        patterns = detector.detect()
        generator = StoryGenerator(evts, chars, patterns, seed)
        story = generator.generate()
        
        full_chronicle.append(f"## {title}\n\n{story}\n\n---\n")

    out_path = Path("SEASON_1_CHRONICLE.md")
    out_path.write_text("\n".join(full_chronicle), encoding='utf-8')
    print(f"\n📘 Chronicle Complete: {out_path.absolute()}")

# --- CLI SETUP ---

def main():
    parser = argparse.ArgumentParser(prog="snowball", description="Council Snowball Fight Simulator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # PLAY
    play_parser = subparsers.add_parser("play", help="Run a simulation session")
    play_parser.add_argument("--seed", type=int, default=42)
    play_parser.add_argument("--turns", type=int, default=20)
    play_parser.add_argument("--mode", default="open")
    play_parser.add_argument("--scenario", default=None)
    play_parser.add_argument("--audit-mode", default="transparent")
    play_parser.add_argument("--generate-story", action="store_true")
    play_parser.add_argument("--story-out", default="story.md")
    play_parser.add_argument("--timeline", type=int, default=0)
    play_parser.add_argument("--samples", action="store_true", help="Force use of sample roster")
    play_parser.add_argument("--summary", choices=['json'], help="Print summary JSON")
    play_parser.set_defaults(func=command_play)

    # VERIFY
    verify_parser = subparsers.add_parser("verify", help="Run verification suites")
    verify_parser.add_argument("target", choices=["chaos", "lock", "audit", "hierarchy", "all"], default="all", nargs="?")
    # These defaults are needed because run_session expects them
    verify_parser.add_argument("--mode", default="open") 
    verify_parser.set_defaults(func=command_verify)

    # CHRONICLE
    chronicle_parser = subparsers.add_parser("chronicle", help="Compile Season 1 Chronicle")
    chronicle_parser.add_argument("--mode", default="open")
    chronicle_parser.set_defaults(func=command_chronicle)

    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
