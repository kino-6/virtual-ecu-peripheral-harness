# Simple Threshold Indicator Specification

This sample is intentionally tiny. It exists to verify the sample workspace,
MBD markup, generated handoff artifacts, and preview report flow without using
thermal-control behavior or a product-like IC specification.

## Intent

- `SIMPLE-001`: When `sampleValue` is greater than or equal to `limit`, the
  controller shall set `active` to true and enter `ACTIVE`.
- `SIMPLE-002`: When `sampleValue` is less than `limit`, the controller shall
  set `active` to false and enter `IDLE`.
- `SIMPLE-003`: The preview report shall show model inputs, scenario steps,
  observed behavior, expected behavior, and pass/fail result.

## Boundary

`ToyInputSource` is a fictional scenario-controlled source. It is not a real
sensor, IC, datasheet, register map, or production-derived interface.

## Review Goal

A reviewer should be able to open the generated demo or report and understand
the complete MBD behavior in under a minute: one input, one parameter, one
output, two states, two rules, and one scenario.
