"""
director.py
The Director (Phase 5) controls the pacing of the narrative.
It decides when to use a Wide Shot (Atmospheric Summary) vs a Close Up (MicroNarrator).
Persona for Wide Shot: Seraphina (T4 Crown Agent).
"""

from typing import List, Dict, Any, Optional
from core.models import Event

class ZoomDirector:
    def __init__(self, narrator):
        self.narrator = narrator
        self.buffer: List[Event] = []
        self.MAX_BUFFER_SIZE = 4
        
    def process(self, events: List[Dict]) -> str:
        story_blocks = []
        self.buffer = []
        snow_net_buffer = []  # Special buffer for Ritual Barrages
        
        for event in events:
            outcome = event.get("outcome", "")
            
            # 0. Check for Ritual Barrage (Snow Net)
            if "SNOW_NET_HIT" in outcome:
                # Flush miss buffer if exists
                if self.buffer:
                    story_blocks.append(self._render_wide_shot())
                
                # Add to net buffer
                snow_net_buffer.append(event)
                continue
            
            # If we hit a non-net event, flush the net buffer
            if snow_net_buffer:
                story_blocks.append(self._render_ritual_barrage(snow_net_buffer))
                snow_net_buffer = []
            
            # Normal Processing
            if self._is_compressible(event):
                self.buffer.append(event)
                if len(self.buffer) >= self.MAX_BUFFER_SIZE:
                    story_blocks.append(self._render_wide_shot())
            else:
                # Flush buffer if exists
                if self.buffer:
                    story_blocks.append(self._render_wide_shot())
                
                # CHECK FOR MIND SHOT (Concise State Updates)
                # If it's a critical state that doesn't need full MicroNarrator drama
                if "PARADOX_CHARGE" in outcome or "LOCK_FADE" in outcome:
                     story_blocks.append(self._render_mind_shot(event))
                
                else:
                    # Render the incompressible event (Close Up / Ceremonial)
                    block = self.narrator.narrate(event)
                    if block:
                        story_blocks.append(block)
                    
        # Final flush
        if self.buffer:
            story_blocks.append(self._render_wide_shot())
        if snow_net_buffer:
             story_blocks.append(self._render_ritual_barrage(snow_net_buffer))
             
        return "\n\n".join(filter(None, story_blocks))

    def _render_mind_shot(self, event: Dict) -> str:
        """
        Renders a concise, internal-monologue style update for state changes.
        """
        outcome = event.get("outcome", "")
        notes = event.get("notes", "")
        
        if "PARADOX_CHARGE" in outcome:
             # Extract budget if possible from notes or logs, but simple is better.
             return f"> *Seraphina hears the hum of rising chaos.* ({notes})"
             
        if "LOCK_FADE" in outcome:
             return f"> *The geometry relaxes. The pattern dissolves into potential.*"
             
        return f"> *{notes}*"

    def _render_ritual_barrage(self, events: List[Dict]) -> str:
        """
        Renders a sequence of SNOW_NET_HIT events as a specific montage beat.
        """
        if not events:
            return ""
            
        count = len(events)
        initiator = events[0].get("thrower", "Unknown")
        tick = events[0].get("tick", 0)
        targets = [e.get("actual", "Unknown") for e in events]
        
        # Scaling Language based on Count (Mega's Rule)
        prose = ""
        if count <= 2:
            prose = f"**Turn {tick}:** The snow tightened. {initiator}'s net caught {', '.join(targets[:2])}, binding them to the pattern."
        elif count == 3:
            prose = f"**Turn {tick}:** {initiator}'s net snapped shut in three directions at once—{', '.join(targets)}—all caught mid-motion as the Weaver's geometry enforced silence."
        else:
             prose = f"**Turn {tick}:** The field went still. {initiator} unleashed a heavy wave of order ({count} targets caught). The simulation paused to acknowledge the weight."
             
        return prose

    def _is_compressible(self, event: Dict) -> bool:
        """
        Determines if an event can be part of a Wide Shot Summary.
        
        HIERARCHY OF IMPORTANCE (The "Mega Rule"):
        1. STATE TRANSITIONS (Rituals, Locks, Fades) -> NEVER compress
        2. HITS (Action Beats) -> NEVER compress (Medium Shot)
        3. MISSES/RICOCHETS -> Compress (Wide Shot)
        """
        context = event.get("context", {})
        outcome = event.get("outcome", "")
        
        # 1. PRIORITY: State Transitions & Rituals
        # These are the narrative anchors. They must be seen.
        
        # Check for Voice Cues (Telemetry's way of flagging importance)
        if context.get("voice_cue"):
            return False
            
        # Check for explicit Phase/State keywords in outcome
        CRITICAL_STATES = [
            "WEAVER",           # Weaver Descends
            "EMERGENCE",        # Emergence Detected
            "PATTERN_LOCK",     # Lock established
            "LOCK_FADE",        # Lock broken/faded
            "CYCLE_RENEWAL",    # Ritual completion
            "PARADOX_CHARGE",   # Significant resource gain
            "BANKAI",           # Ultimate State
            "JOGRESS"           # Fusion State
        ]
        
        if any(state in outcome for state in CRITICAL_STATES):
            return False

        # 2. PRIORITY: Action Beats (Hits)
        # Hits change the score and emotional state.
        if "HIT" in outcome and "RICOCHET" not in outcome and "SNOW_NET" not in outcome:
            # Note: SNOW_NET_HIT is usually spammy, but usually comes in blocks. 
            # If we want to compress snow nets, we'd need special logic.
            # For now, let's keep literal HITs as action beats.
            return False
            
        # 3. PRIORITY: Compression Candidates (The "Boring" Stuff)
        if "MISS" in outcome or "RICOCHET" in outcome or "SNOW_NET_HIT" in outcome:
            # We allow SNOW_NET_HIT to be compressed? 
            # Actually, the user log showed them as separate lines. 
            # Let's keep SNOW_NET_HIT as compressible only if we want to summarize "The barrage".
            # For now, let's stick to safe compression.
            return True
            
        # Default: If we don't know what it is, show it to be safe.
        return False

    def _render_wide_shot(self) -> str:
        """
        Synthesizes the buffered events into an Atmospheric Summary.
        Voice: Seraphina (The System/Observer).
        """
        if not self.buffer:
            return ""
            
        start_tick = self.buffer[0].get("tick")
        end_tick = self.buffer[-1].get("tick")
        count = len(self.buffer)
        
        # Analyze the batch
        misses = sum(1 for e in self.buffer if "MISS" in e.get("outcome", ""))
        ricochets = sum(1 for e in self.buffer if "RICOCHET" in e.get("outcome", ""))
        
        # Seraphina's Voice Logic
        prose = ""
        if count == 1:
            e = self.buffer[0]
            thrower = e.get("thrower", "Unknown")
            prose = f"**Turn {start_tick}:** {thrower} threw wide. The pattern remained undisturbed."
        
        elif misses == count:
            prose = f"**Turns {start_tick}-{end_tick}:** The volley continued without consequence. {count} throws drifted harmlessly into the white void, the Council testing range rather than intent."
            
        elif ricochets > 0:
            prose = f"**Turns {start_tick}-{end_tick}:** Chaos without connection. Returns were exchanged, resulting in {ricochets} glancing blows but no solid impacts. The energy was frantic but unanchored."
            
        else:
            prose = f"**Turns {start_tick}-{end_tick}:** The simulation settled into a rhythm. Snow flew across the arena, marking time but not score."
            
        self.buffer = [] # clear
        return prose
