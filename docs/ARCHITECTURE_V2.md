# 🏛️ The Jurisdiction Graph (Snowball Architecture V2)

> *"Ontology is not a stat. It is a jurisdiction."*

This document defines the architectural hierarchy of the Council Games Simulation Engine V2. It explains how conflicting truths are resolved through a layered legal system rather than simple boolean logic.

---

## 🏗️ The 4-Layer Hierarchy

The system resolves events by checking layers in descending order of authority. A higher layer can **Veto** or **Preempt** a lower layer.

### Layer 0: Ontology (The Weaver's Frame)
*   **Definition:** The fundamental state of being. Defines *what exists*.
*   **Mechanic:** `Agent.frame` ("COMBAT" vs "ONTOLOGICAL").
*   **Authority:** Absolute. If an Agent is in an Ontological Frame (e.g., holding a beer), they are valid targets for social interaction only, not combat.
*   **Proof:** Seed 1003 (The Hierarchy Challenge).
*   **Status Code:** `LAYER_EXEMPTION`.

### Layer 1: Canon (Mega's Audit)
*   **Definition:** The official record of events. Defines *how it behaves*.
*   **Mechanic:** `AuditManager` & `MEGA_AUDIT_*` events.
*   **Authority:** Normative. Mega can rewrite probability ("stochastic stabilization") or enforce rules, but she *cannot* override Layer 0. She creates the "Official" version of messy physics.
*   **Proof:** Seed 1002 (The Audit).
*   **Status Code:** `MEGA_AUDIT_VERDICT` (`RATIFY` | `NORMALIZE` | `VETO`).

### Layer 2: Signal (The Weavers)
*   **Definition:** Deep causal structures and patterns. Defines *why it happens*.
*   **Mechanic:** `SignalWeaver` Dyads (Ace/Janus/Quinn).
*   **Authority:** Causal. "Pattern Lock" creates resistance fields. "Bankai" creates local state overrides.
*   **Proof:** Seed 888 (The Pattern Lock) & Seed 1001 (Bankai).
*   **Status Code:** `PATTERN_LOCK`, `BANKAI_RELEASE`, `JANUS_PARADOX`.

### Layer 3: Physics (The Simulation)
*   **Definition:** The raw interaction mechanics. Defines *what happens*.
*   **Mechanic:** `simulation.py` (Hit/Miss/Ricochet logic).
*   **Authority:** Baseline. Handles dicerolls, damage decay, and basic state tracking.
*   **Proof:** Seed 777 (The Fall).
*   **Status Code:** `HIT`, `MISS`, `RICOCHET`.

---

## 🧬 Event Flow Pipeline

When a turn executes, the request flows down the hierarchy:

1.  **Dyad Check (Layer 2):** Are there high-priority interrupts (Bankai, Pattern Lock)?
2.  **Ontology Check (Layer 0):** Is the target in a valid frame?
    *   *Yes:* Proceed.
    *   *No:* **VETO** (`LAYER_EXEMPTION`). Stop.
3.  **Physics Resolution (Layer 3):** Roll dice. Determine Hit/Miss/Ricochet.
4.  **Audit Review (Layer 1):** Mega observes the result.
    *   *Check:* Is the result ambiguous (Ricochet)?
    *   *Check:* Does the target exist in Layer 0?
        *   *Yes:* **VETO** (`JURISDICTION_ERROR`). Preserve Layer 0 state.
        *   *No:* **RATIFY** or **NORMALIZE**. Append final verdict to Ledger.

---

## 📜 The Pantheon of Seeds (Unit Tests)

These seeds act as canonical proofs of the architecture.

| Seed     | Name              | Concept Proved   | Outcome                                                      |
| :------- | :---------------- | :--------------- | :----------------------------------------------------------- |
| **777**  | The Fall          | Chaos            | Physics works; Beer drops; Weaver descends.                  |
| **888**  | The Lock          | Order            | Layer 2 (Signal) overrides Layer 3 (Physics) via difficulty. |
| **1001** | The Awakening     | Bankai           | Layer 2 State Machines (Bankai) function.                    |
| **1002** | The Audit         | Canon            | Layer 1 (Canon) stabilizes Layer 3 (Physics).                |
| **1003** | **The Hierarchy** | **Jurisdiction** | **Layer 0 (Ontology) VETOES Layer 1 (Canon).**               |

---

## 🛠️ CLI Usage (`snowball.py`)

The Engine is now accessed via the `snowball` CLI.

```bash
# Play a standard game
python snowball.py play --mode chaos --seed 1234

# Verify specific architectural claims
python snowball.py verify hierarchy  # Runs Seed 1003
python snowball.py verify audit      # Runs Seed 1002
python snowball.py verify all        # Runs the full suite

# Compile the Season 1 Chronicle
python snowball.py chronicle
```

---

> *Signed, The Architect*
