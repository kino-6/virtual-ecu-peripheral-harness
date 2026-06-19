# Simple Threshold Indicator

Fictional minimal MBD authoring source. This file is not the rendered MBD model
deliverable; it is the structured text input parsed into an internal IR and
then exported to reviewable/generated artifacts such as `generated/demo.html`,
Simulink `.m`, Modelica, SCXML, FMI metadata, and reports.

The supported subset below captures the model semantics needed by the demo:
component ports and parameters, state handoff, functional allocation, data
flow, priority-ordered control rules, and harness boundaries. This sample is
deliberately small and does not describe a real IC, datasheet, ECU, company,
production project, safety case, or certified code generator.

```mbd-component
component ToyThresholdIndicator
trace SIMPLE-001 SIMPLE-002 SIMPLE-003
bus virtual mode=preview wordBits=8
parameter limit: count = 10

port in sampleValue: count = 0
port out active: bool = false
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 active reset=0
```

```mbd-state
IDLE --> ACTIVE: sampleValue >= limit trace SIMPLE-001
ACTIVE --> IDLE: sampleValue < limit trace SIMPLE-002
```

```mbd-decomposition
function ThresholdCompare: responsibility=Compare sampleValue against limit and own the active decision; owns=active,ACTIVE,IDLE; inputs=sampleValue,limit; outputs=active,state; trace=SIMPLE-001,SIMPLE-002,SIMPLE-003; scenarios=above_limit
```

```mbd-flow
ToyInputSource.sampleValue -> ThresholdCompare.sampleValue: scenario input trace SIMPLE-001
ToyThresholdIndicator.limit -> ThresholdCompare.limit: threshold parameter trace SIMPLE-001 SIMPLE-002
ThresholdCompare.active -> ToyThresholdIndicator.active: comparison result trace SIMPLE-001 SIMPLE-002
ToyThresholdIndicator.active -> ScenarioReport.observedBehavior: reported output trace SIMPLE-003
```

```mbd-control
priority 10 rule activate: owner ThresholdCompare from * when sampleValue >= limit then state=ACTIVE, active=true trace SIMPLE-001 SIMPLE-003 scenarios above_limit
priority 20 rule clear: owner ThresholdCompare from * when sampleValue < limit then state=IDLE, active=false trace SIMPLE-002 SIMPLE-003
```

```mbd-harness
device ToyInputSource role=source boundary=virtual_ic trace SIMPLE-001
ecu ToyThresholdIndicator role=controller boundary=hal trace SIMPLE-001 SIMPLE-002 SIMPLE-003
```
