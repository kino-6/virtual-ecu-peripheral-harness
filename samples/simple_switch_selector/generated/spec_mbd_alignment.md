# Spec To MBD Semantic Alignment

Spec: `/Users/kinoshitayuki/work/virtual-ecu-peripheral-harness/samples/simple_switch_selector/spec.md`
MBD source: `/Users/kinoshitayuki/work/virtual-ecu-peripheral-harness/samples/simple_switch_selector/model.mbd.md`

Spec-to-MBD semantic alignment: **PASS**

## Matched nodes
- `Constant: highValue = 100`
- `Constant: lowValue = 25`
- `Input Port: selectHigh`
- `Output selectedValue = highValue`
- `Output selectedValue = lowValue`
- `ScenarioReport.observedBehavior`
- `ToySelectorSource`
- `selectHigh == true?`

## Matched edges
- `Constant: highValue = 100 --> selectHigh == true?`
- `Constant: lowValue = 25 --> selectHigh == true?`
- `Input Port: selectHigh --> selectHigh == true?`
- `Output selectedValue = highValue --> ScenarioReport.observedBehavior`
- `Output selectedValue = lowValue --> ScenarioReport.observedBehavior`
- `ToySelectorSource --selectHigh--> Input Port: selectHigh`
- `selectHigh == true? --false--> Output selectedValue = lowValue`
- `selectHigh == true? --true--> Output selectedValue = highValue`

## Missing MBD nodes
- None

## Extra MBD nodes
- None

## Missing MBD edges
- None

## Extra MBD edges
- None
