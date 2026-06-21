# Mermaid To MBD Coverage Task Archive

Archived from `Tasks.md` after completing the state-machine review material,
Mermaid-to-MBD item expansion, and repository-defined 34/34 MVP coverage work.

- Phase 26: Reworked state-machine review material around transition-system
  review, state inventories, transition tables, diagnostics, action semantics,
  and scenario walk-through evidence.
- Phase 27: Added `Constant: <name> = <value>` support and documented the
  supported Mermaid-to-MBD item subset.
- Phase 28: Added logical `and`, `or`, and unary `not` expression coverage
  across parsing, preview runtime, and Simulink handoff.
- Phase 29: Locked the 34-item MVP coverage contract with stable IDs and drift
  tests.
- Phase 30: Added arithmetic dataflow coverage for `Gain`, `Sum`, and
  `Product`.
- Phase 31: Added limit and lookup coverage for `Saturation` and `Lookup1D`.
- Phase 32: Added structural composition coverage for multiple functions,
  one-level subsystem naming, and bus/vector signal notation.
- Phase 33: Added state `entry`, `during`, and `exit` action coverage.
- Phase 34: Added MVP handoff handling for hierarchy, parallel separators,
  shallow history, and temporal event state semantics.

All phases were completed with focused tests, full `pytest`, and `git diff
--check` at the time they were archived.
