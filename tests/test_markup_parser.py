from pathlib import Path

from veph.markup_parser import parse_markup, parse_markup_file
from veph.sample_catalog import load_sample


ROOT = Path(__file__).resolve().parents[1]


def test_markup_file_parses_to_internal_ir():
    model = parse_markup_file(load_sample("toy_power_monitor", ROOT).paths.model)

    assert model.title == "Toy Power Monitor IC"
    assert model.component.name == "ToyPowerMonitorIC"
    assert model.component.bus["type"] == "spi"
    assert model.ports["voltage"].direction == "in"
    assert model.ports["ready"].type == "bool"
    assert model.registers["STATUS"].fields["ready"].bit == 7
    assert model.registers["CONTROL"].access == "rw"
    assert model.transitions[0].source == "RESET"
    assert model.transitions[0].target == "INIT"
    assert model.flows[0].source == "ECU_App.control_task"
    assert model.flows[0].target == "HAL_SPI"
    assert model.source_path.name == "model.mbd.md"


def test_internal_ir_json_is_not_public_authoring_format():
    model = parse_markup_file(load_sample("toy_power_monitor", ROOT).paths.model)

    data = model.to_dict()

    assert data["metadata"]["sourceFormat"] == "mbd-markdown"
    assert data["metadata"]["irRole"] == "internal snapshot"
    assert data["component"]["name"] == "ToyPowerMonitorIC"


def test_thermal_fan_markup_keeps_requirement_traceability():
    model = parse_markup_file(load_sample("thermal_fan_control", ROOT).paths.model)

    assert model.component.name == "ToyThermalFanController"
    assert "SYS-001" in model.component.trace
    assert model.ports["temperatureC"].direction == "in"
    assert model.registers["TEMP_STATUS"].fields["valid"].bit == 15
    assert model.controls[0].name == "sensorFault"
    assert model.controls[0].actions["fanDuty"] == "safeDuty"
    assert "SYS-005" in model.controls[0].trace
    assert model.harness_devices[0].name == "ToyTempSensorIC"
    assert model.harness_devices[0].boundary == "virtual_ic"
    assert "HAR-001" in model.flows[0].trace
    assert "HAR-005" in model.to_dict()["metadata"]["requirementRefs"]


def test_thermal_protection_markup_matches_spec_recovery_and_trace_shape():
    model = parse_markup_file(load_sample("thermal_protection_controller", ROOT).paths.model)

    recover_rule = next(control for control in model.controls if control.name == "recoverFromLatch")
    fault_function = next(function for function in model.functions if function.name == "FaultLatchRecoveryManager")
    recover_transition = next(
        transition
        for transition in model.transitions
        if transition.source == "FAULT_LATCHED" and transition.target == "IDLE"
    )

    assert len(model.functions) == 7
    assert fault_function.responsibility == "Own sensor fault latch hold and explicit recovery behavior"
    assert "SENSOR_FAULT" in fault_function.owns
    assert "SYS-008" in fault_function.trace
    assert "thermal_protection_recovery" in fault_function.scenarios
    assert recover_rule.priority == 10
    assert recover_rule.owner == "FaultLatchRecoveryManager"
    assert recover_rule.state_scope == "FAULT_LATCHED"
    assert "invalidDebounced == false" in recover_rule.condition
    assert recover_rule.condition_expr.kind == "logical"
    assert recover_rule.condition_expr.operator == "and"
    assert [operand.kind for operand in recover_rule.condition_expr.operands] == [
        "comparison",
        "comparison",
        "comparison",
    ]
    assert "invalidDebounced == false" in recover_transition.condition
    assert "SYS-008" in recover_rule.trace
    assert recover_rule.scenarios == ["thermal_protection_recovery"]
    assert next(control for control in model.controls if control.name == "holdLatchedFault").condition == "always"
    assert [control.priority for control in model.controls] == sorted(control.priority for control in model.controls)
    assert all(control.scenarios for control in model.controls)
    assert all(control.owner for control in model.controls)
    assert {control.owner for control in model.controls} <= {function.name for function in model.functions}
    assert all(not ref.startswith("SYS-") for ref in model.component.trace)


def test_markup_parser_supports_unary_not_expression():
    model = parse_markup(
        """# Logical Not

```mbd-component
component LogicalNot
bus virtual mode=preview wordBits=8

port in inhibit: bool = false
port out active: bool = false
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 active reset=0
```

```mbd-state
note: no state machine
```

```mbd-flow
LogicalNot.inhibit -> Logic.inhibit: input
Logic.active -> LogicalNot.active: output
```

```mbd-control
priority 10 rule enable: owner Logic from * when not inhibit then active=true
```
""",
        ROOT / "samples" / "logical_not" / "model.mbd.md",
    )

    expression = model.controls[0].condition_expr
    assert expression.kind == "logical"
    assert expression.operator == "not"
    assert expression.operands[0].kind == "variable"
    assert expression.operands[0].name == "inhibit"
