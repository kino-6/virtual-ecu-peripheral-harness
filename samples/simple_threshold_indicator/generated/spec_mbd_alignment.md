# Spec To MBD Semantic Alignment

Spec: `/Users/kinoshitayuki/work/virtual-ecu-peripheral-harness/samples/simple_threshold_indicator/spec.md`
MBD source: `/Users/kinoshitayuki/work/virtual-ecu-peripheral-harness/samples/simple_threshold_indicator/model.mbd.md`

Spec-to-MBD semantic alignment: **PASS**

## Matched nodes
- `Input Port: sampleValue`
- `Output active = false`
- `Output active = true`
- `Parameter: limit`
- `ScenarioReport.observedBehavior`
- `ToyInputSource`
- `sampleValue >= limit?`

## Matched edges
- `Input Port: sampleValue --> sampleValue >= limit?`
- `Output active = false --> ScenarioReport.observedBehavior`
- `Output active = true --> ScenarioReport.observedBehavior`
- `Parameter: limit --> sampleValue >= limit?`
- `ToyInputSource --sampleValue--> Input Port: sampleValue`
- `sampleValue >= limit? --false--> Output active = false`
- `sampleValue >= limit? --true--> Output active = true`

## Missing MBD nodes
- None

## Extra MBD nodes
- None

## Missing MBD edges
- None

## Extra MBD edges
- None
