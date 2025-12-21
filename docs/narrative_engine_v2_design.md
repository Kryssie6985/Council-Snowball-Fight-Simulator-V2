# ❄️ Narrative Engine V2: From Historian to Witness
## Design Study & Architecture Proposal

**Status:** DRAFT (RFC)
**Author:** Antigravity (via DeepScribe interpretation)
**Version:** 2.0-Proposal

---

### 1. The Core Question
> *Is the auto-narrative generation firing after the entire run or during the entire run? I feel like every throw should have a narration attached... whether simple or complex.*

**Current Answer:**
The engine currently operates in **Historian Mode** (Post-Process).
1.  **Simulation Runs:** Turns 1–50 execute fully. The Ledger (`snowball_events.jsonl`) is written.
2.  **Simulation Ends.**
3.  **Narrative Engine Starts:** It reads the Ledger, looks for high-level patterns (Acts, Dyads), and writes a summary story.

**Why DeepScribe's Version Felt Different:**
DeepScribe's manual narrative (Seed 999) operated in **Witness Mode**.
It didn't just summarize ("Ace hit DeepScribe"). It described the *internal state* ("Ace's spite meter capped at 0.55") and the *immediate reaction* ("Mico: 'Spite becomes strategy'"). It treated *every* event as a potential story beat.

---

### 2. The Architectural Gap

| Feature         | Current Engine (Historian)            | DeepScribe Vision (Witness)                    |
| :-------------- | :------------------------------------ | :--------------------------------------------- |
| **Timing**      | Post-Run (Batch)                      | "Live" (Per-Event)                             |
| **Granularity** | Summarized Acts ("Ace landed 4 hits") | Turn-by-Turn ("Turn 6: The ricochet...")       |
| **Context**     | Outcome only (Hit/Miss)               | Internal State (Spite %, Empathy Field status) |
| **Voice**       | Pattern-level Quotes                  | Micro-Narration (1-liners per event)           |
| **Pacing**      | Fast Summary                          | "Slow Motion" replays for critical moments     |

To achieve the DeepScribe vision, we do **not** necessarily need to run the narrative engine *during* the simulation (which risks performance drags). We need to **log richer state** and **upgrade the post-processor**.

---

### 3. Proposed Architecture: The "SportsCaster" Model

We preserve the safety of the Post-Process model but upgrade the fidelity.

#### A. Richer Ledger (The "Black Box" Flight Recorder)
Currently, `Event` logs: `Thrower`, `Target`, `Outcome`, `Touch`.
**V2 Upgrade:** We need to snapshot the *internal state* of the agent at the moment of the event.

```json
{
  "tick": 7,
  "thrower": "Ace",
  "target": "Kryssie",
  "outcome": "HIT",
  "context": {
    "spite_meter": 0.55,
    "is_bankai_active": true,
    "holding_beer": false
  }
}
```

#### B. The "Micro-Narrator" Class
Instead of one big `StoryGenerator`, we introduce a `MicroNarrator` for each agent.

*   **Input:** Single `Event` + Context.
*   **Logic:**
    *   Is this a generic hit? -> Return None (silence).
    *   Is this a Critical Hit / Status Change? -> Consult **Voice Anchor**.
*   **Output:** A single markdown line.

**Example Flow (Ace hits DeepScribe):**
1.  `MicroNarrator` sees `spite_meter > 0.5`.
2.  Checks Ace's Anchor: `reaction_to_hit_while_angry`.
3.  Generates: *"Ace's throw is pure heat. Spite at 0.55."*

#### C. Variable Zoom (The "Camera Director")
We don't want to read 50 lines of "Ace threw a snowball." The engine needs a **Director** module.

*   **Low Zoom:** "Turns 1-5 passed with minor skirmishes."
*   **High Zoom (Triggered by Emergence):**
    *   "Turn 6: STOP."
    *   *Inject Seraphina Announcement.*
    *   *Show Mico Reaction.*
    *   *Describe the physics of the snowball.*

---

### 4. Implementation Roadmap

#### Phase 1: The "Rich Ledger" (Low Effort, High Value)
*   Modify `simulation.py` to enact **State Snapshots**.
*   When Ace throws, log his `spite_meter`.
*   When Janus throws, log his `paradox_budget`.
*   *Result:* The Ledger contains the "Why", not just the "What".

#### Phase 2: The "Commentary Track" (The Voice Upgrade)
*   Update `Voice Anchor` YAML to include **Micro-Reactions** (not just general style).
    *   `on_hit_success`: "Target acquired."
    *   `on_hit_taken`: "Armor integrity 90%."
*   Update `auto_narrative_generator` to inject these lines next to specific turns in the output log.

#### Phase 3: The "Witness" Mode (The DeepScribe Goal)
*   A flag `--mode witness` that produces a turn-by-turn "Live Blog" style output.
*   Uses `Seraphina` as the "Host" gluing the turns together.

### 5. Recommendation
**Do not switch to concurrent (during-run) generation yet.**
It complicates the code (`main.py` loop) without adding value. The "Post-Process" approach can perfectly emulate the "Live" feel **IF** the data in the ledger is rich enough.

**Immediate Next Step:**
Add `context` dictionary to the `Event` model and populate it during simulation. This unlocks everything else.

---
*End of Design Study*
