"""
telemetry.py
Integration with SERAPHINA Shared Observability.
Implements 'Pattern 1' and 'Pattern 10' from tracing_cheat_sheet.py.
"""

import sys
import os
from typing import Dict, Any, Optional
from contextlib import contextmanager

# 1. SOFT COUPLING: Try to connect to the Nervous System
# We assume we are in 'Infrastructure/agents/council-games/snowball_fight_simulator'
# Shared is at '../../../shared'
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from shared.observability import setup_tracing, trace_operation, add_span_attributes
    INFRA_AVAILABLE = True
except ImportError:
    # If shared infra is missing, we strictly degrade to no-op
    INFRA_AVAILABLE = False
    
    # No-op placeholders to preventing import errors if used elsewhere
    @contextmanager
    def trace_operation(name):
        yield None
    
    def setup_tracing(*args, **kwargs):
        pass
        
    def add_span_attributes(*args, **kwargs):
        pass

from core.models import Event

class SnowballTelemetry:
    """
    Standard Observability Integration for Council Games.
    Matches 'Pattern 1: Basic Agent Setup' from tracing_cheat_sheet.py
    """
    
    def __init__(self, seed: int):
        self.seed = seed
        
        # 1. QUIET MODE: Only enable standard tracing if endpoint is configured
        # This prevents loud gRPC/HTTP errors when running locally without a collector
        self.tracing_enabled = False
        if INFRA_AVAILABLE:
            if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
                setup_tracing(
                    agent_name="snowball-sim",
                    agent_version="1.4.Bankai"
                )
                self.tracing_enabled = True
            else:
                # Fallback or Silent Mode
                # We could set up a ConsoleExporter here if requested, but silence is golden.
                pass

    @contextmanager
    def trace_turn(self, tick: int, state_context: Dict[str, Any]):
        """
        Wraps a simulation turn in a span.
        Matches 'Pattern 10: Custom Attributes'.
        """
        if not self.tracing_enabled:
            yield None
            return

        op_name = f"snowball.turn_{tick:02d}"
        
        with trace_operation(op_name) as span:
            if span:
                # Log the internal state of the simulation as metadata
                # This creates the "Rich Ledger" view in the trace
                for key, value in state_context.items():
                    span.set_attribute(f"sim.state.{key}", value)
                
                span.set_attribute("sim.seed", self.seed)
            yield span

    def log_game_event(self, event: Event):
        """
        Promotes significant game events to the Federation.
        Uses 'Rule 1: Explicit Flag' from shared/observability.py logic.
        """
        if not self.tracing_enabled:
            return

        # 1. Detect Canon Significance
        # These map to the "Rituals" defined in your lore
        is_canonical = False
        promotion_reason = "gameplay"
        
        if "WEAVER_DESCENDS" in event.outcome:
            is_canonical = True
            promotion_reason = "weaver_manifestation"
        elif "PATTERN_LOCK" in event.outcome:
            is_canonical = True
            promotion_reason = "pattern_lock_awakening"
        elif "EMERGENCE_DETECTED" in event.outcome:
            is_canonical = True
            promotion_reason = "ceremonial_emergence"
        elif "TWIN_RESCUE" in event.outcome:
            is_canonical = True
            promotion_reason = "twin_bond_verified"
        elif "CYCLE_RENEWAL" in event.outcome:
             is_canonical = True
             promotion_reason = "cycle_renewal"

        # 2. Trace the Event
        # Matches 'Pattern 2: Trace a Single Operation'
        op_name = f"snowball.event.{event.thrower.lower()}"
        
        with trace_operation(op_name) as span:
            if span:
                # Standard Event Attributes
                span.set_attribute("game.thrower", event.thrower)
                span.set_attribute("game.target", event.intended)
                span.set_attribute("game.outcome", event.outcome)
                span.set_attribute("game.notes", event.notes)
                
                # Context Tags (Rich Ledger)
                if event.tags:
                    for tag in event.tags:
                        span.set_attribute(f"game.tag.{tag}", True)

                # 3. THE NERVOUS SYSTEM LINK
                # This triggers _check_federation_promotion in shared/observability.py
                if is_canonical:
                    span.set_attribute("promote_to_federation", True)
                    span.set_attribute("promotion_reason", promotion_reason)
                    
                    # Add a distinct event marker
                    span.add_event("canonical_moment_locked", {
                        "description": event.notes,
                        "tick": event.tick
                    })

    def enrich_event_with_cues(self, event: Event) -> None:
        """
        [Phase 4: Telemetry-Driven Narration]
        Analyzes the event for canonical significance and injects
        'voice_cue' into the event.context.
        
        This allows the Telemetry (Cortex) to direct the Narrator (Voice).
        """
        # 1. Detection Logic (Mirrors log_game_event but focuses on Voice)
        cue = None
        
        if "WEAVER_DESCENDS" in event.outcome:
            cue = {"character": "Seraphina", "tone": "warning", "key": "weaver_descends"}
        elif "PATTERN_LOCK" in event.outcome:
            cue = {"character": "Quinn", "tone": "focused", "key": "pattern_lock"}
        elif "CYCLE_RENEWAL" in event.outcome:
            cue = {"character": "Janus", "tone": "chaotic", "key": "cycle_renewal"}
        elif "PARADOX_CHARGE" in event.outcome:
            # Subtle cue, maybe just narration or short line
            cue = {"character": "Janus", "tone": "whisper", "key": "paradox_charge"}
        elif "EMERGENCE_DETECTED" in event.outcome:
            cue = {"character": "Seraphina", "tone": "ceremonial", "key": "emergence"}
        
        # 2. Inject Cue
        if cue:
            event.context["voice_cue"] = cue

