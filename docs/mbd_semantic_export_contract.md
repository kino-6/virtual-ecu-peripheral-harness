# MBD Semantic Export Contract

This contract defines the supported semantic subset for generated MBD handoff
artifacts. It is intentionally smaller than general Simulink, Stateflow,
Modelica, or FMI capability.

## Artifact Classes

- Review-only artifact: preserves model information for human inspection, but
  does not claim executable semantics. Markdown, HTML, Mermaid, PlantUML, and
  comments in generated handoff files are review-only unless backed by the
  semantic subset below.
- Semantic handoff artifact: represents supported MBD behavior structurally
  using tool concepts such as typed ports, constants, compare blocks, logical
  blocks, switches, and state transition annotations. Generated Simulink `.m`
  is the first semantic handoff target in this repository.
- Executable preview subset: local Python/C preview used for smoke scenarios.
  It is not a certified code generator or verification backend.

## Supported Semantic Subset

The semantic handoff subset supports:

- Inport and Outport blocks for model ports.
- Parameter values represented as Constant blocks or model workspace entries.
- Constant blocks for numeric and boolean literals.
- Compare blocks for simple comparisons.
- Switch blocks or If/Action-style structures for guarded rule selection.
- Boolean literals: `true`, `false`.
- Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.
- Logical operators: `and`, `or`.
- Priority-ordered control rules, where lower numeric priority wins.
- State transition handoff as explicit comments or table annotations tied to
  the same control-rule source.

## Expression Grammar

Supported control conditions are:

```text
always
variable
number
true | false
left == right
left != right
left < right
left <= right
left > right
left >= right
expr and expr
expr or expr
```

Operands may be variables, numeric literals, or boolean literals. Parentheses,
arithmetic, function calls, bit operations, timing operators, and custom
operators are unsupported.

## Memory And Hysteresis

Simple hysteresis may be represented only as priority-ordered control rules
over explicit state scope and threshold comparisons. Hidden memory, delays,
debounce timing, counters, sample-time semantics, and latch internals are
unsupported unless they are represented as explicit model inputs or state-scope
handoff annotations.

Unsupported behavior must be reported explicitly. Exporters must not silently
downgrade unsupported control behavior into comments.

## Simulink Handoff Minimum

For each supported control rule, generated Simulink `.m` must include structural
blocks for:

- The input signals used by the guard.
- Parameter or literal constants used by the guard and actions.
- Compare blocks for comparison expressions.
- Logical blocks for `and` or `or` expressions.
- Switch or If/Action-style blocks for output action selection.

Traceability comments remain required, but comments are not sufficient as the
primary semantic carrier.
