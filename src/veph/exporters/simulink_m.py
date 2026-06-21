from __future__ import annotations

from veph.ir import ControlRuleIR, ExpressionIR, MbdModelIR
from veph.model_loader import PeripheralModel


class SimulinkSemanticExportError(ValueError):
    """Raised when MBD semantics cannot be represented in the Simulink subset."""


def export_simulink_m(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        _validate_semantic_subset(model)
        lines = [
            f"% Generated from Mermaid-like MBD markup for {model.component.name}.",
            "% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.",
            "% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.",
            f"model = '{model.component.name}Model';",
            "new_system(model);",
            "open_system(model);",
        ]
        signal_blocks = _emit_ports(lines, model)
        parameter_blocks = _emit_parameters(lines, model)
        available_blocks = {**signal_blocks, **parameter_blocks}
        if not model.controls:
            _emit_default_output_values(lines, model, signal_blocks)
        lines.append("% Semantic control structure. Lower numeric priority wins.")
        for index, control in enumerate(sorted(model.controls, key=lambda item: (item.priority, item.name))):
            condition_block = _emit_condition(lines, control, available_blocks, index)
            _emit_action_switches(lines, model, control, condition_block, signal_blocks, parameter_blocks, index)
            lines.append(
                f"% priority {control.priority} {control.name}: owner {control.owner or 'unallocated'} from {control.state_scope} "
                f"when {control.condition} then {control.actions} scenarios {control.scenarios}"
            )
        lines.append("% Functional decomposition summary:")
        for function in model.functions:
            lines.append(
                f"% function {function.name}: owns {function.owns}; inputs {function.inputs}; outputs {function.outputs}"
            )
        lines.append("% Flow handoff summary:")
        for flow in model.flows:
            lines.append(f"% flow {flow.source} -> {flow.target}: {flow.label}")
        lines.append("% State transition summary:")
        for transition in model.transitions:
            lines.append(f"% {transition.source} -> {transition.target} when {transition.condition}")
        lines.append("save_system(model);")
        return "\n".join(lines) + "\n"

    system_name = model.name.replace("IC", "Model")
    lines = [
        f"% Generated from fictional Textual MBD model {model.name}.",
        "% Canonical source: Textual MBD YAML. Regenerate instead of editing as source.",
        "% This best-effort script requires MATLAB/Simulink if executed.",
        f"model = '{system_name}';",
        "new_system(model);",
        "open_system(model);",
        f"add_block('simulink/Sources/Constant', [model '/Voltage']);",
        f"add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/UndervoltageThreshold']);",
        f"set_param([model '/UndervoltageThreshold'], 'const', '{model.parameters.get('undervoltageThreshold', 7.0)}');",
        f"add_block('simulink/Sinks/Display', [model '/StatusDisplay']);",
        f"add_line(model, 'Voltage/1', 'UndervoltageThreshold/1');",
        f"add_line(model, 'UndervoltageThreshold/1', 'StatusDisplay/1');",
        "% State machine summary:",
    ]
    for transition in model.states.transitions:
        lines.append(f"% {transition.source} -> {transition.target} when {transition.when}")
    lines.append("save_system(model);")
    return "\n".join(lines) + "\n"


def _validate_semantic_subset(model: MbdModelIR) -> None:
    for control in model.controls:
        _validate_expression(control.condition_expr, control)
        for output_name in control.actions:
            if output_name != "state" and output_name not in model.ports:
                raise SimulinkSemanticExportError(
                    f"control rule {control.name!r} action {output_name!r} is not a model output port; "
                    "only output-port actions can be structurally exported"
                )


def _validate_expression(expression: ExpressionIR, control: ControlRuleIR) -> None:
    if expression.kind == "unsupported":
        raise SimulinkSemanticExportError(
            f"control rule {control.name!r} has unsupported condition {control.condition!r}: "
            f"{expression.diagnostic or 'unsupported expression'}"
        )
    if expression.kind in {"always", "variable", "number", "boolean"}:
        return
    if expression.kind == "comparison":
        if expression.operator not in {"==", "!=", "<", "<=", ">", ">="}:
            raise SimulinkSemanticExportError(
                f"control rule {control.name!r} uses unsupported comparison operator {expression.operator!r}"
            )
        if expression.left is None or expression.right is None:
            raise SimulinkSemanticExportError(f"control rule {control.name!r} has an incomplete comparison")
        if expression.left.kind != "variable":
            raise SimulinkSemanticExportError(
                f"control rule {control.name!r} comparison must use a variable on the left side"
            )
        if expression.right.kind not in {"variable", "number", "boolean"}:
            raise SimulinkSemanticExportError(
                f"control rule {control.name!r} comparison right side must be a variable, number, or boolean"
            )
        return
    if expression.kind == "logical":
        if expression.operator not in {"and", "or", "not"}:
            raise SimulinkSemanticExportError(
                f"control rule {control.name!r} uses unsupported logical operator {expression.operator!r}"
            )
        if not expression.operands:
            raise SimulinkSemanticExportError(f"control rule {control.name!r} has an empty logical expression")
        if expression.operator == "not" and len(expression.operands) != 1:
            raise SimulinkSemanticExportError(f"control rule {control.name!r} has an invalid not expression")
        for operand in expression.operands:
            _validate_expression(operand, control)
        return
    raise SimulinkSemanticExportError(
        f"control rule {control.name!r} has unsupported expression kind {expression.kind!r}"
    )


def _emit_ports(lines: list[str], model: MbdModelIR) -> dict[str, str]:
    signal_blocks: dict[str, str] = {}
    input_index = 0
    output_index = 0
    for port in model.ports.values():
        safe = _simulink_block_name(port.name)
        if port.direction == "in":
            y = 70 + input_index * 70
            lines.append(f"add_block('simulink/Sources/In1', [model '/In_{safe}']);")
            lines.append(f"set_param([model '/In_{safe}'], 'Position', [40 {y} 90 {y + 25}]);")
            lines.append(f"set_param([model '/In_{safe}'], 'OutDataTypeStr', '{_simulink_type(port.type)}');")
            signal_blocks[port.name] = f"In_{safe}"
            input_index += 1
        elif port.direction == "out":
            y = 70 + output_index * 70
            lines.append(f"add_block('simulink/Sinks/Out1', [model '/Out_{safe}']);")
            lines.append(f"set_param([model '/Out_{safe}'], 'Position', [900 {y} 950 {y + 25}]);")
            lines.append(f"set_param([model '/Out_{safe}'], 'OutDataTypeStr', '{_simulink_type(port.type)}');")
            signal_blocks[port.name] = f"Out_{safe}"
            output_index += 1
    return signal_blocks


def _emit_parameters(lines: list[str], model: MbdModelIR) -> dict[str, str]:
    parameter_blocks: dict[str, str] = {}
    for index, parameter in enumerate(model.component.parameters.values()):
        safe = _simulink_block_name(parameter.name)
        y = 70 + index * 55
        lines.append(f"add_block('simulink/Sources/Constant', [model '/Param_{safe}']);")
        lines.append(f"set_param([model '/Param_{safe}'], 'Value', '{parameter.default}');")
        lines.append(f"set_param([model '/Param_{safe}'], 'OutDataTypeStr', '{_simulink_type(parameter.type)}');")
        lines.append(f"set_param([model '/Param_{safe}'], 'Position', [180 {y} 260 {y + 30}]);")
        parameter_blocks[parameter.name] = f"Param_{safe}"
    return parameter_blocks


def _emit_default_output_values(lines: list[str], model: MbdModelIR, signal_blocks: dict[str, str]) -> None:
    for index, port in enumerate(port for port in model.ports.values() if port.direction == "out"):
        block = _simulink_block_name(f"Default_{port.name}")
        y = 480 + index * 45
        _emit_constant(lines, block, _matlab_literal(port.default or "0"), port.type, [520, y, 620, y + 30])
        lines.append(f"add_line(model, '{block}/1', '{signal_blocks[port.name]}/1', 'autorouting', 'on');")


def _emit_condition(
    lines: list[str],
    control: ControlRuleIR,
    available_blocks: dict[str, str],
    index: int,
) -> str:
    return _emit_expression(lines, control.condition_expr, control, available_blocks, f"Rule_{control.name}", 360 + index * 140)


def _emit_expression(
    lines: list[str],
    expression: ExpressionIR,
    control: ControlRuleIR,
    available_blocks: dict[str, str],
    prefix: str,
    y: int,
) -> str:
    safe_prefix = _simulink_block_name(prefix)
    if expression.kind == "always":
        block = f"{safe_prefix}_AlwaysTrue"
        _emit_constant(lines, block, "true", "boolean", [320, y, 390, y + 30])
        return block
    if expression.kind == "variable":
        if expression.name not in available_blocks:
            raise SimulinkSemanticExportError(
                f"control rule {control.name!r} references unknown variable {expression.name!r}"
            )
        return available_blocks[expression.name]
    if expression.kind in {"number", "boolean"}:
        block = f"{safe_prefix}_Literal"
        _emit_constant(lines, block, _literal_value(expression), _literal_type(expression), [320, y, 390, y + 30])
        return block
    if expression.kind == "comparison":
        return _emit_comparison(lines, expression, control, available_blocks, safe_prefix, y)
    if expression.kind == "logical":
        operand_blocks = [
            _emit_expression(lines, operand, control, available_blocks, f"{safe_prefix}_{position}", y + position * 42)
            for position, operand in enumerate(expression.operands, start=1)
        ]
        block = f"{safe_prefix}_{expression.operator.upper()}"
        lines.append(f"add_block('simulink/Logic and Bit Operations/Logical Operator', [model '/{block}']);")
        lines.append(f"set_param([model '/{block}'], 'Operator', '{expression.operator.upper()}');")
        if expression.operator != "not":
            lines.append(f"set_param([model '/{block}'], 'Inputs', '{len(operand_blocks)}');")
        lines.append(f"set_param([model '/{block}'], 'Position', [590 {y} 660 {y + 40}]);")
        for port_index, operand_block in enumerate(operand_blocks, start=1):
            lines.append(f"add_line(model, '{operand_block}/1', '{block}/{port_index}', 'autorouting', 'on');")
        return block
    raise SimulinkSemanticExportError(
        f"control rule {control.name!r} has unsupported expression kind {expression.kind!r}"
    )


def _emit_comparison(
    lines: list[str],
    expression: ExpressionIR,
    control: ControlRuleIR,
    available_blocks: dict[str, str],
    prefix: str,
    y: int,
) -> str:
    assert expression.left is not None
    assert expression.right is not None
    if expression.left.name not in available_blocks:
        raise SimulinkSemanticExportError(
            f"control rule {control.name!r} references unknown variable {expression.left.name!r}"
        )
    block = f"{prefix}_Compare"
    lines.append(f"add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/{block}']);")
    lines.append(f"set_param([model '/{block}'], 'relop', '{expression.operator}');")
    lines.append(f"set_param([model '/{block}'], 'const', '{_comparison_constant(expression.right)}');")
    lines.append(f"set_param([model '/{block}'], 'Position', [420 {y} 540 {y + 45}]);")
    lines.append(f"add_line(model, '{available_blocks[expression.left.name]}/1', '{block}/1', 'autorouting', 'on');")
    return block


def _emit_action_switches(
    lines: list[str],
    model: MbdModelIR,
    control: ControlRuleIR,
    condition_block: str,
    signal_blocks: dict[str, str],
    parameter_blocks: dict[str, str],
    index: int,
) -> None:
    action_index = 0
    for output_name, value in control.actions.items():
        if output_name == "state":
            lines.append(f"% state handoff {control.name}: next state {value}")
            continue
        output_block = signal_blocks[output_name]
        true_block = _action_value_block(lines, control, output_name, value, parameter_blocks, index, action_index)
        false_block = _default_value_block(lines, model, output_name, index, action_index)
        switch_block = _simulink_block_name(f"Rule_{control.name}_{output_name}_Switch")
        y = 360 + index * 140 + action_index * 26
        lines.append(f"add_block('simulink/Signal Routing/Switch', [model '/{switch_block}']);")
        lines.append(f"set_param([model '/{switch_block}'], 'Threshold', '0.5');")
        lines.append(f"set_param([model '/{switch_block}'], 'Position', [720 {y} 800 {y + 45}]);")
        lines.append(f"add_line(model, '{true_block}/1', '{switch_block}/1', 'autorouting', 'on');")
        lines.append(f"add_line(model, '{condition_block}/1', '{switch_block}/2', 'autorouting', 'on');")
        lines.append(f"add_line(model, '{false_block}/1', '{switch_block}/3', 'autorouting', 'on');")
        lines.append(f"add_line(model, '{switch_block}/1', '{output_block}/1', 'autorouting', 'on');")
        action_index += 1


def _action_value_block(
    lines: list[str],
    control: ControlRuleIR,
    output_name: str,
    value: str,
    parameter_blocks: dict[str, str],
    rule_index: int,
    action_index: int,
) -> str:
    if value in parameter_blocks:
        return parameter_blocks[value]
    block = _simulink_block_name(f"Rule_{control.name}_{output_name}_{value}_Const")
    y = 920 + rule_index * 80 + action_index * 35
    _emit_constant(lines, block, _matlab_literal(value), _infer_literal_type(value), [560, y, 660, y + 30])
    return block


def _default_value_block(
    lines: list[str],
    model: MbdModelIR,
    output_name: str,
    rule_index: int,
    action_index: int,
) -> str:
    port = model.ports[output_name]
    value = port.default or "0"
    block = _simulink_block_name(f"Default_{output_name}_{rule_index}_{action_index}")
    y = 1120 + rule_index * 80 + action_index * 35
    _emit_constant(lines, block, _matlab_literal(value), port.type, [560, y, 660, y + 30])
    return block


def _emit_constant(lines: list[str], block: str, value: str, type_name: str, position: list[int]) -> None:
    lines.append(f"add_block('simulink/Sources/Constant', [model '/{block}']);")
    lines.append(f"set_param([model '/{block}'], 'Value', '{value}');")
    lines.append(f"set_param([model '/{block}'], 'OutDataTypeStr', '{_simulink_type(type_name)}');")
    lines.append(f"set_param([model '/{block}'], 'Position', [{position[0]} {position[1]} {position[2]} {position[3]}]);")


def _comparison_constant(expression: ExpressionIR) -> str:
    if expression.kind == "variable":
        return expression.name
    return _literal_value(expression)


def _literal_value(expression: ExpressionIR) -> str:
    if expression.kind == "boolean":
        return "true" if expression.value is True else "false"
    return str(expression.value)


def _literal_type(expression: ExpressionIR) -> str:
    return "boolean" if expression.kind == "boolean" else "double"


def _matlab_literal(value: str) -> str:
    if value.lower() in {"true", "false"}:
        return value.lower()
    return value


def _infer_literal_type(value: str) -> str:
    if value.lower() in {"true", "false"}:
        return "boolean"
    return "double"


def _simulink_type(type_name: str) -> str:
    if type_name in {"bool", "boolean"}:
        return "boolean"
    return "double"


def _simulink_block_name(name: str) -> str:
    safe = name.replace(".", "_").replace(" ", "_").replace("-", "_")
    return "".join(character if character.isalnum() or character == "_" else "_" for character in safe)
