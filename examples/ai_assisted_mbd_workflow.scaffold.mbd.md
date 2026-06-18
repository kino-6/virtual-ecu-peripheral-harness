# MBD Scaffold

> Generated scaffold from requirements. Do not treat this scaffold as approved behavior
> until open questions are reviewed.

## Review Status

- Behavior approval: **PENDING**
- Coverage meaning: traces identify intended coverage, not accepted model semantics.
- TODO values are explicit placeholders, not accepted demo answers.
- External MBD/product-test infrastructure is still required for production-grade verification.

## Requirement Coverage Intent

- `SYS-001`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-002`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-003`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-004`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-005`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-006`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-007`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-008`: scaffold coverage required; refine into concrete model element before approval.
- `SYS-009`: scaffold coverage required; refine into concrete model element before approval.
- `SWE-001`: scaffold coverage required; refine into concrete model element before approval.
- `SWE-002`: scaffold coverage required; refine into concrete model element before approval.
- `SWE-003`: scaffold coverage required; refine into concrete model element before approval.
- `SWE-004`: scaffold coverage required; refine into concrete model element before approval.
- `SWE-005`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-001`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-002`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-003`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-004`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-005`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-006`: scaffold coverage required; refine into concrete model element before approval.
- `ENG-007`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-001`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-002`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-003`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-004`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-005`: scaffold coverage required; refine into concrete model element before approval.
- `CGEN-006`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-001`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-002`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-003`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-004`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-005`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-006`: scaffold coverage required; refine into concrete model element before approval.
- `HAR-007`: scaffold coverage required; refine into concrete model element before approval.

```mbd-component
component ToyThermalProtectionController
trace SYS-001 SYS-002 SYS-003 SYS-004 SYS-005 SYS-006 SYS-007 SYS-008
bus virtual mode=preview wordBits=16
parameter TODO_highThreshold: degC = 0
parameter TODO_lowThreshold: degC = 0
parameter TODO_deratingLimit: percent = 0
parameter TODO_safeCommand: percent = 0

port in temperatureC: degC = 0
port in temperatureValid: bool = true
port out coolingCommand: percent = 0
port out deratingCommand: percent = 0
port out diagnosticFault: bool = false
```

```mbd-state
RESET --> NOMINAL: open-question SYS-008 trace SYS-008
NOMINAL --> COOLING: open-question threshold-high trace SYS-003
COOLING --> DERATING: open-question derating-entry trace SYS-005
DERATING --> FAULT_LATCHED: open-question persistent-invalid-sensor trace SYS-007
FAULT_LATCHED --> NOMINAL: open-question recovery-conditions trace SYS-008
```

```mbd-flow
ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample trace SYS-001 HAR-001
HAL_SPI.read_temperature -> ToyThermalProtectionController.temperatureC: HAL input trace SWE-004 HAR-002
ToyThermalProtectionController.coolingCommand -> HAL_PWM.set_cooling: virtual actuator command trace SYS-002 HAR-001
ToyThermalProtectionController.deratingCommand -> ToyLoadLimiterIC.limit: virtual load limiter command trace SYS-005 HAR-006
```

```mbd-control
rule TODO_sensorFault: when temperatureValid == false then diagnosticFault=true trace SYS-006 SYS-007
rule TODO_highTemperature: when temperatureC >= TODO_highThreshold then coolingCommand=TODO trace SYS-003
rule TODO_derating: when temperatureC >= TODO_deratingEntry then deratingCommand=TODO trace SYS-005
```

```mbd-harness
device ToyTempSensorIC role=sensor boundary=virtual_ic trace HAR-001 HAR-006
device ToyFanDriverIC role=actuator boundary=virtual_ic trace HAR-001
device ToyLoadLimiterIC role=actuator boundary=virtual_ic trace HAR-006
ecu ToyThermalProtectionController role=controller boundary=hal trace HAR-002 SWE-004
```

## Open Questions

Do not invent missing thresholds, timings, recovery rules, or fault semantics.

- open-question SYS-005: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-006: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-007: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-008: define explicit state/control/harness/scenario/expected behavior coverage.
