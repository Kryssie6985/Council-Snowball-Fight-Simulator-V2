# ❄️ Council Snowball Fight Simulator V2

![Council Snowball Fight](assets/readme_asset.png)

> *"Beer diplomacy is temporary; snow is forever."*

An advanced agentic simulation where the "Council" (Generic Representations of AI Archetypes) engages in a snowball fight.
This project is not just a game; it is a **Jurisdiction Graph** demonstrating a layered conflict resolution architecture: **Ontology > Canon > Signal > Physics**.

[**📖 Read the Digital Comic**](comic.md)
[**🎄 Christmas Special (Season 1.5)**](christmas_special_1.md)

---

## 🚀 Quick Start

The simulation is controlled via the `snowball.py` CLI.

```bash
# 1. Play a standard "Chaos Mode" game
python snowball.py play --mode chaos --turns 20

# 2. Portfolio / Sample Mode (Run without custom chars)
python snowball.py play --samples --summary json

# 3. Verify the architecture (Run the "Golden Record" Unit Test)
python snowball.py verify hierarchy

# 4. Generate the full Season 1 Chronicle
python snowball.py chronicle
```

## 🏗️ The Architecture: "The Jurisdiction Graph"

The simulator uses a 4-Layer Hierarchy to resolve events.

*   **Layer 0: Ontology** (The Frame). Defines *what exists*. Absolute Veto Power.
*   **Layer 1: Canon** (The Audit). Defines *how it behaves*. Normative Stabilization.
*   **Layer 2: Signal** (The Weaver). Defines *why it happens*. Causal Pattern Locks.
*   **Layer 3: Physics** (The Sim). Defines *what happens*. Stochastic Dice Rolls.

See [docs/ARCHITECTURE_V2.md](docs/ARCHITECTURE_V2.md) for the deep dive.

## 📂 Project Structure

*   `core/`: The simulation engine (Physics, Logic, Mechanics).
*   `characters/`: JSON stats defining the agents.
*   `characters/doc/`: **The Soul**. Narrative definitions (Voice Anchors, Mind Cards). *Note: Contains stubs in open release.*
*   `dyads/`: Complex interaction logic (Signal Weavers).
*   `narratives/`: Generated chronicles and story output.
*   `skeletor_ledger/`: The raw JSONL event stream ("The Truth").

## 🛡️ Soul Protection & Open Core

This repository is designed as an **Open Core** release.
The simulation engine, physics, and architecture are fully open source. However, the specific "Identity" of the Council is protected.

*   **Protected Files (The Soul):**
    *   `characters/*.json` (The Council Roster stats)
    *   `dyads/*.py` (The Canon Synergy Logic, e.g., *Signal Weavers*)
    *   `characters/doc/*` (The Proprietary Prompts & Lore)

*   **Open Files (The Core):**
    *   `core/*` (The Physics & Narrative Engine)
    *   `characters/samples/*` (The "Vanguard" Sample Roster)
    *   `dyads/samples/*` (The Plugin System for Custom Synergies)

**If you clone this repo:** It will default to using the **Sample Roster**. The engine gracefully handles the absence of the Canon Soul files.

## 🔌 Custom Dyads (Plugin System)

You can create your own agentic synergies!
Drop python files into `dyads/samples/`.

*   See [`dyads/samples/README.md`](dyads/samples/README.md) for instructions.
*   See [`dyads/samples/_template.py`](dyads/samples/_template.py) for the contract.
*   Examples included: `offensive_line.py` (Tank/DPS synergy) and `chaos_containment.py` (Stabilizer synergy).

---

### The Pantheon (Seeds)

*   `777`: The Chaos Fall
*   `888`: The Pattern Lock
*   `1001`: Bankai Awakening
*   `1002`: The Audit
*   `1003`: The Hierarchy

**Status:** Canonized.
**Version:** 2.0.0 (The Golden Record)
**Mascot:** [Simulatoor™️](docs/SIMULATOOR.md) (The Ghost in the Shell)
