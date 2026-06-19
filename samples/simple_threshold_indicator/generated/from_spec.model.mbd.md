# Simple Threshold Indicator Specification

Generated from Spec Mermaid Design Overview in `/Users/kinoshitayuki/work/virtual-ecu-peripheral-harness/samples/simple_threshold_indicator/spec.md`.
This file is deterministic authoring source for generated MBD review artifacts.

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
IDLE --> ACTIVE: sampleValue >= limit trace SIMPLE-001 SIMPLE-003
ACTIVE --> IDLE: sampleValue < limit trace SIMPLE-002 SIMPLE-003
```

```mbd-decomposition
function Compare: responsibility=Evaluate sampleValue >= limit and map decision branches to outputs; owns=active,ACTIVE,IDLE; inputs=sampleValue,limit; outputs=active; trace=SIMPLE-001,SIMPLE-002,SIMPLE-003; scenarios=above_limit
```

```mbd-flow
ToyInputSource.sampleValue -> Compare.sampleValue: scenario input trace SIMPLE-001
ToyThresholdIndicator.limit -> Compare.limit: threshold parameter trace SIMPLE-001 SIMPLE-002
Compare.active -> ToyThresholdIndicator.active: comparison result trace SIMPLE-001 SIMPLE-002
ToyThresholdIndicator.active -> ScenarioReport.observedBehavior: reported output trace SIMPLE-003
```

```mbd-control
priority 10 rule active_true: owner Compare from * when sampleValue >= limit then state=ACTIVE, active=true trace SIMPLE-001 SIMPLE-003 scenarios above_limit
priority 20 rule active_false: owner Compare from * when sampleValue < limit then state=IDLE, active=false trace SIMPLE-002 SIMPLE-003
```

```mbd-harness
device ToyInputSource role=source boundary=virtual_ic trace SIMPLE-001
ecu ToyThresholdIndicator role=controller boundary=hal trace SIMPLE-001 SIMPLE-002 SIMPLE-003
```
