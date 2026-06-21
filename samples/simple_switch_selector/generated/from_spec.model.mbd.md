# Simple Switch Selector Specification

Generated from Spec Mermaid Design Overview in `samples/simple_switch_selector/spec.md`.
This file is deterministic authoring source for generated MBD review artifacts.

```mbd-component
component ToySwitchSelector
trace SWS-001 SWS-002 SWS-003 SWS-004
bus virtual mode=preview wordBits=8
parameter highValue: count = 100
parameter lowValue: count = 25

port in selectHigh: bool = false
port out selectedValue: count = 25
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 selectedValue reset=0
```

```mbd-state
note: no state diagram declared in spec
```

```mbd-decomposition
function Decision: responsibility=Evaluate selectHigh == true and map decision branches to outputs; owns=selectedValue; inputs=selectHigh,highValue,lowValue; outputs=selectedValue; trace=SWS-001,SWS-002,SWS-003,SWS-004; scenarios=select_high
```

```mbd-flow
ToySelectorSource.selectHigh -> Decision.selectHigh: scenario input trace SWS-001
ToySwitchSelector.highValue -> Decision.highValue: constant value trace SWS-001 SWS-002
ToySwitchSelector.lowValue -> Decision.lowValue: constant value trace SWS-001 SWS-002
Decision.selectedValue -> ToySwitchSelector.selectedValue: comparison result trace SWS-001 SWS-002
ToySwitchSelector.selectedValue -> ScenarioReport.observedBehavior: reported output trace SWS-004
```

```mbd-control
priority 10 rule selectedValue_true: owner Decision from * when selectHigh == true then selectedValue=highValue trace SWS-001 SWS-004 scenarios select_high
priority 20 rule selectedValue_false: owner Decision from * when selectHigh != true then selectedValue=lowValue trace SWS-002 SWS-004
```

```mbd-harness
device ToySelectorSource role=source boundary=virtual_ic trace SWS-001
ecu ToySwitchSelector role=controller boundary=hal trace SWS-001 SWS-002 SWS-003 SWS-004
```
