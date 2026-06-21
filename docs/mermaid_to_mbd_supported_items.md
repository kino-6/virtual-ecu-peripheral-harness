# Mermaid To MBD Supported Items

This document defines the supported `Spec.md` Mermaid subset that the script
can convert into MBD authoring Markdown. The subset is intentionally small and
fictional-sample oriented.

## Flowchart Items

| Mermaid writing style | Meaning | Converted MBD element | Covered by |
| --- | --- | --- | --- |
| `source[ToySource]` | Fictional scenario source or named block | Harness source / flow source | `simple_threshold_indicator`, `simple_switch_selector`, `simple_state_machine`, `simple_relay_hysteresis` |
| `input[Input Port: sampleValue]` | Model input port | `port in sampleValue` | `simple_threshold_indicator`, `simple_switch_selector`, `simple_state_machine`, `simple_relay_hysteresis` |
| `limit[Parameter: limit]` | Tunable model parameter | `parameter limit` plus parameter flow | `simple_threshold_indicator`, `simple_relay_hysteresis` |
| `high[Constant: highValue = 100]` | Fixed value source | Current IR stores this as `parameter highValue = 100` plus a `constant value` flow label | `simple_switch_selector` |
| `compare{sampleValue >= limit?}` | Decision / guard | `mbd-control when sampleValue >= limit` | `simple_threshold_indicator`, `simple_switch_selector` |
| `decision{enable == true or force == true?}` | Logical guard with `and` / `or` / unary `not` | Parsed expression IR, preview evaluation, and Simulink Logical Operator handoff | `tests/test_spec_mbd_conversion.py`, `tests/test_preview_runtime.py`, `tests/test_exporters.py` |
| `decision -->|true| active[Output active = true]` | Branch output action | `then active=true` | `simple_threshold_indicator`, `simple_switch_selector` |
| `machine --> busy[Output busy]` | State-machine output port | `port out busy` | `simple_state_machine`, `simple_relay_hysteresis` |
| `active --> report[ScenarioReport.observedBehavior]` | Report evidence endpoint | `mbd-flow` to report evidence | all current converted samples |
| `relay[ToyRelayController]` between inputs and outputs | Controller/function block | `mbd-decomposition function ToyRelayController` | `simple_state_machine`, `simple_relay_hysteresis` |

## State Diagram Items

| Mermaid writing style | Meaning | Converted MBD element | Covered by |
| --- | --- | --- | --- |
| `stateDiagram-v2` | Flat state-machine section | `mbd-state` section | `simple_threshold_indicator`, `simple_state_machine`, `simple_relay_hysteresis` |
| `[*] --> IDLE` | Initial state | `spec-initial IDLE` in review context; first generated state is used by preview | state-machine converted samples |
| `IDLE --> RUNNING: startCommand == true` | State-scoped transition | `mbd-state` transition plus matching `mbd-control from IDLE when ...` | `simple_state_machine` |
| `OFF --> ON: level >= onThreshold` | Threshold transition with parameter | `mbd-state` transition and state-scoped control rule | `simple_relay_hysteresis` |

## Why `Constant` Was Added

The current converter already handled `Parameter: <name>`, but that made fixed
branch values look tunable. For simple Switch-style models, a reviewer often
wants to distinguish:

- tunable threshold: `Parameter: limit`
- fixed branch value: `Constant: highValue = 100`

The current internal IR does not yet have a separate Constant type, so
`Constant` is represented as a parameter value with a `constant value` flow
label. This is deliberately a transitional mapping: the Mermaid authoring
surface and alignment report preserve the `Constant` semantics, while the
runtime/export path stays small.

## Coverage Summary

- Conversion tests: `tests/test_spec_mbd_conversion.py`
- Spec/MBD alignment tests: `tests/test_spec_mbd_alignment.py`
- Sample determinism tests:
  - `tests/test_simple_threshold_sample.py`
  - `tests/test_simple_switch_sample.py`
  - `tests/test_simple_state_machine_sample.py`
  - `tests/test_simple_relay_hysteresis_sample.py`
- Generated review artifact checks: sample-specific tests assert the generated
  MBD, viewer/review HTML, reports, and handoff artifacts remain deterministic.

This is feature coverage, not proof of broad Mermaid support. The supported
subset is exactly the documented patterns above plus their tested combinations.

## Coverage Matrix

| ID | Area | Item | Status | Evidence |
| --- | --- | --- | --- | --- |
| MBD-MVP-01 | Interfaces and value sources | Input port | supported | sample `simple_threshold_indicator`; tests `test_spec_mbd_conversion.py` |
| MBD-MVP-02 | Interfaces and value sources | Output port | supported | sample `simple_threshold_indicator`; tests `test_spec_mbd_conversion.py` |
| MBD-MVP-03 | Interfaces and value sources | Tunable parameter | supported | sample `simple_threshold_indicator`; tests `test_spec_mbd_alignment.py` |
| MBD-MVP-04 | Interfaces and value sources | Fixed constant | supported | sample `simple_switch_selector`; tests `test_simple_switch_sample.py` |
| MBD-MVP-05 | Combinational decision logic | Comparison guard | supported | sample `simple_threshold_indicator`; tests `test_spec_mbd_conversion.py` |
| MBD-MVP-06 | Combinational decision logic | Boolean literal | supported | sample `simple_switch_selector`; tests `test_preview_runtime.py` |
| MBD-MVP-07 | Combinational decision logic | True/false branch | supported | sample `simple_threshold_indicator`; tests `test_spec_mbd_alignment.py` |
| MBD-MVP-08 | Combinational decision logic | Switch-style selected output | supported | sample `simple_switch_selector`; tests `test_simple_switch_sample.py` |
| MBD-MVP-09 | Combinational decision logic | Logical `and` | supported | tests `test_spec_mbd_conversion.py` and `test_preview_runtime.py` |
| MBD-MVP-10 | Combinational decision logic | Logical `or` | supported | tests `test_spec_mbd_conversion.py` and `test_exporters.py` |
| MBD-MVP-11 | Combinational decision logic | Logical `not` | supported | tests `test_markup_parser.py` and `test_exporters.py` |
| MBD-MVP-12 | Combinational decision logic | Arithmetic expression | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-13 | Combinational decision logic | Saturation/min/max | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-14 | Combinational decision logic | Lookup table | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-15 | State-machine logic | Flat state | supported | sample `simple_state_machine`; tests `test_simple_state_machine_sample.py` |
| MBD-MVP-16 | State-machine logic | Initial state | supported | sample `simple_state_machine`; tests `test_simple_state_machine_sample.py` |
| MBD-MVP-17 | State-machine logic | Guarded transition | supported | sample `simple_state_machine`; tests `test_spec_mbd_conversion.py` |
| MBD-MVP-18 | State-machine logic | State-scoped action | supported | sample `simple_state_machine`; tests `test_simple_state_machine_sample.py` |
| MBD-MVP-19 | State-machine logic | Implicit self-hold note | supported | sample `simple_state_machine`; explicit review artifact evidence |
| MBD-MVP-20 | State-machine logic | Entry/during/exit action | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-21 | State-machine logic | Hierarchy | supported | tests `test_spec_mbd_conversion.py`; MVP handoff note |
| MBD-MVP-22 | State-machine logic | Parallel state | supported | tests `test_spec_mbd_conversion.py`; MVP handoff note |
| MBD-MVP-23 | State-machine logic | History | supported | tests `test_spec_mbd_conversion.py`; MVP handoff note |
| MBD-MVP-24 | State-machine logic | Temporal event | supported | tests `test_spec_mbd_conversion.py`; MVP handoff note |
| MBD-MVP-25 | Trace and review evidence | Requirement ID extraction | supported | sample specs; tests `test_requirements_scaffold.py` |
| MBD-MVP-26 | Trace and review evidence | Trace-intent mapping | supported | sample `simple_state_machine`; tests `test_simple_state_machine_sample.py` |
| MBD-MVP-27 | Trace and review evidence | Report endpoint | supported | all current converted samples; tests `test_spec_mbd_alignment.py` |
| MBD-MVP-28 | Trace and review evidence | Scenario link | supported | sample manifests; tests `test_sample_catalog.py` |
| MBD-MVP-29 | Trace and review evidence | Pass/fail report summary | supported | preview reports; tests `test_simple_relay_hysteresis_sample.py` |
| MBD-MVP-30 | Structural composition | One controller/function node | supported | sample `simple_state_machine`; tests `test_spec_mbd_conversion.py` |
| MBD-MVP-31 | Structural composition | Multiple functions | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-32 | Structural composition | Subsystem hierarchy | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-33 | Structural composition | Bus/vector signal | supported | tests `test_spec_mbd_conversion.py` |
| MBD-MVP-34 | Structural composition | Typed scalar signal | supported | sample ports; tests `test_markup_parser.py` |

## Coverage Against Basic MBD Expressions

There is no single universal denominator for "MBD basic expressions." Against
the full Simulink/Stateflow ecosystem, this project is intentionally tiny. The
useful denominator for this repository is a small control-logic MVP subset:
discrete inputs, parameters/constants, simple guards, simple decisions, flat
state transitions, review trace, and preview scenarios.

### Current MVP Coverage Estimate

| Area | Basic expression items counted for this MVP | Supported now | Coverage |
| --- | --- | ---: | ---: |
| Interfaces and value sources | input port, output port, tunable parameter, fixed constant | 4 / 4 | 100% |
| Combinational decision logic | comparison guard, boolean literal, true/false branch, switch-style selected output, logical `and`, logical `or`, logical `not`, arithmetic expression, saturation/min/max, lookup table | 10 / 10 | 100% |
| State-machine logic | flat state, initial state, guarded transition, state-scoped action, implicit self-hold note, entry/during/exit action, hierarchy, parallel state, history, temporal event | 10 / 10 | 100% |
| Trace and review evidence | requirement ID extraction, trace-intent mapping, report endpoint, scenario link, pass/fail report summary | 5 / 5 | 100% |
| Structural composition | one controller/function node, multiple functions, subsystem hierarchy, bus/vector signal, typed scalar signal | 5 / 5 | 100% |

Overall for this deliberately small MVP catalog: **34 / 34 items** are
supported or explicitly represented, **100%** of this repository-defined MVP
catalog. This number is only useful inside this repository
because the catalog is intentionally narrow.

### Coverage Against Full MBD Tools

Against broad Simulink/Stateflow modeling, coverage is very low, likely under
**5%**. The converter does not attempt to cover full block libraries, solvers,
continuous dynamics, physical modeling, full Stateflow action language, truth
tables, data dictionaries, variants, buses, fixed-point configuration, code
generation settings, or tool qualification workflows.

### Why The Current Items Were Added

The implemented items were chosen to unlock a reviewable requirements-to-MBD
loop, not to clone Simulink:

1. `Input Port`, `Output`, `Parameter`, and `ScenarioReport` establish the
   review boundary.
2. Decision nodes and branch output actions establish the smallest useful
   compare/switch subset.
3. `stateDiagram-v2` establishes the smallest useful flat state-machine subset.
4. `Constant` was added after `simple_switch_selector` exposed a modeling
   ambiguity: fixed branch values should not look like tunable thresholds.
5. Harness report summaries were added because review needs observed vs
   expected behavior, not just diagrams.

Next likely high-value coverage items beyond this MVP are `Multiport Switch`,
`Unit Delay`/memory, richer bus objects, and stricter Stateflow action timing.

## Current Boundaries

Unsupported Mermaid semantics must fail or remain explicit review questions.
The MVP represents hierarchy, parallel separators, shallow history, and temporal
events as handoff notes, not as full executable Stateflow semantics. The
converter still does not support loops with backtracking semantics, physical
plant modeling, real hardware details, or certified execution semantics.
