# Custom Dyads (Samples)

This directory allows you to define custom Dyad interactions (pairs of agents with special synergies) without modifying the core codebase.

## How to Create a Custom Dyad

1.  Create a new Python file in this directory (e.g., `my_custom_dyad.py`).
2.  Define a class that implements the Dyad protocol (use `_template.py` as a guide).
3.  Implement a static method `check_requirements(roster)` to tell the system when to activate.

## The Dyad Contract

Your class must implement:

*   `check_requirements(roster: Dict[str, Agent]) -> bool` (Static)
*   `on_turn_start(ctx) -> List[Event]`
*   `on_hit(ctx, thrower_id, target_id) -> List[Event]`
*   `on_turn_end(ctx) -> List[Event]`

See `_template.py` for a full working example.
