# Simple Switch Selector

Fictional minimal MBD authoring source for a Switch-style selector sample.
This file is not the rendered MBD model deliverable; it is the structured text
input parsed into an internal IR and then exported to generated review and
handoff artifacts.

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
  bit 0 selectedValue reset=25
```

```mbd-state
note: no state machine; this sample reviews simple compare/switch data flow
```

```mbd-decomposition
function SwitchSelector: responsibility=Compare selectHigh and select highValue or lowValue using Switch-style simple conditional logic; owns=selectedValue; inputs=selectHigh,highValue,lowValue; outputs=selectedValue; trace=SWS-001,SWS-002,SWS-003,SWS-004; scenarios=select_high
```

```mbd-flow
ToySelectorSource.selectHigh -> SwitchSelector.selectHigh: selector input trace SWS-001 SWS-002 SWS-003
ToySwitchSelector.highValue -> SwitchSelector.highValue: high constant value trace SWS-001 SWS-003
ToySwitchSelector.lowValue -> SwitchSelector.lowValue: low constant value trace SWS-002 SWS-003
SwitchSelector.selectedValue -> ToySwitchSelector.selectedValue: selected output trace SWS-001 SWS-002
ToySwitchSelector.selectedValue -> ScenarioReport.observedBehavior: reported selected value trace SWS-004
```

```mbd-control
priority 10 rule select_high_value: owner SwitchSelector from * when selectHigh == true then selectedValue=highValue trace SWS-001 SWS-003 SWS-004 scenarios select_high
priority 20 rule select_low_value: owner SwitchSelector from * when selectHigh != true then selectedValue=lowValue trace SWS-002 SWS-003 SWS-004 scenarios select_high
```

```mbd-harness
device ToySelectorSource role=source boundary=virtual_ic trace SWS-001 SWS-002 SWS-003
ecu ToySwitchSelector role=controller boundary=hal trace SWS-001 SWS-002 SWS-003 SWS-004
```
