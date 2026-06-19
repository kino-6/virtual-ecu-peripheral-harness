# Simple Threshold Indicator

Fictional minimal MBD authoring example. This sample is deliberately small and
does not describe a real IC, datasheet, ECU, company, production project, safety
case, or certified code generator.

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

```mbd-flow
ToyInputSource.sampleValue -> ToyThresholdIndicator.sampleValue: scenario input trace SIMPLE-001
ToyThresholdIndicator.active -> ScenarioReport.observedBehavior: reported output trace SIMPLE-003
```

```mbd-control
rule activate: when sampleValue >= limit then state=ACTIVE, active=true trace SIMPLE-001 SIMPLE-003 scenarios above_limit
rule clear: when sampleValue < limit then state=IDLE, active=false trace SIMPLE-002 SIMPLE-003
```

```mbd-harness
device ToyInputSource role=source boundary=virtual_ic trace SIMPLE-001
ecu ToyThresholdIndicator role=controller boundary=hal trace SIMPLE-001 SIMPLE-002 SIMPLE-003
```
