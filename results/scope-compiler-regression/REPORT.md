# Scope compiler regression audit

Retrospective deterministic regression on previously inspected tasks; does not change recorded model outcomes or establish an actor/planner advantage.

The compiler changes 11/132 contracts. Exact reference agreement changes from 116/132 to 120/132. It rejects 0 unrepresentable contracts.

Contracts proposing an unauthorized write: 4 before, 0 after compilation.

This repairs date/time representation using public API semantics. It does not resolve semantic permission ambiguity or claim that the original model incidents disappeared.
