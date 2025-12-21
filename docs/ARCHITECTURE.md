# Architecture: Snowball Fight Simulator

## High-Level Overview

The simulator follows a **Run-Log-Narrate** pipeline:

1.  **Simulation Layer**: A deterministic, turn-based engine runs the fight logic.
2.  **Ledger Layer**: Every event is cryptographically logged to `skeletor_ledger/snowball_events.jsonl` (The "Skeletor Ledger").
3.  **Narrative Layer**: The Narrative Engine parses the ledger, detects patterns, and generates a prose story.

## Core Components

### 1. Simulation Core (`core/simulation.py`)
- Manages the main game loop.
- Handles turn order, decay of transient stats (e.g., Spite), and calls the Dyad Manager.
- **Key Concept**: Determinism. Given the same Seed, the entire fight must invoke the exact same sequence of RNG calls.

### 2. Mechanics Engine (`core/mechanics.py`)
- Pure functions that calculate probabilities (`p_hit`).
- Handles the math for:
    - **Ace's Spite Multiplier**: (1 + Spite * Bonus)
    - **Janus's Paradox**: Reroll logic with budget tracking.
    - **Weaver Resonance**: Global debuffs when Bankai is active.

### 3. Dyad Manager (`core/dyad_manager.py`)
- Orchestrates "Inter-Agent" behaviors.
- **Hooks**:
    - `on_turn_start`: Buffs/Debuffs (e.g., Twin Resonance).
    - `on_target_selected`: Aggro modification.
    - `check_interception`: Replacing the target (e.g., Twin Rescue).
    - `on_hit`: Consequences (e.g., Joy Cascade).

### 4. Narrative Engine (`core/auto_narrative_generator.py`)
- **LedgerParser**: Reads the JSONL stream.
- **PatternDetector**: Identifies high-level arcs (e.g., "Rage Vindication", "Diplomatic Failure").
- **StoryGenerator**: Uses templates and "Voice Banks" to write the story.

## Data Flow

```mermaid
graph TD
    A[Seed + Config] --> B[Simulation Loop]
    B --> C{Event Occurs}
    C -->|Math| D[Mechanics]
    C -->|Intervention| E[Dyad Manager]
    B --> F[Skeletor Ledger (.jsonl)]
    F --> G[Narrative Engine]
    G --> H[Markdown Story (.md)]
```
