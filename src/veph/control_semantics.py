from __future__ import annotations

from veph.ir import ControlRuleIR, ExpressionIR, FlowIR, MbdModelIR


def find_threshold_pair(controls: list[ControlRuleIR]) -> tuple[ControlRuleIR, ControlRuleIR] | None:
    for first in controls:
        first_key = comparison_key(first.condition_expr)
        if first_key is None:
            continue
        for second in controls:
            if first is second:
                continue
            second_key = comparison_key(second.condition_expr)
            if second_key is None:
                continue
            left, right, operator = first_key
            if (left, right) == second_key[:2] and is_complement(operator, second_key[2]):
                return (first, second) if first.priority <= second.priority else (second, first)
    return None


def comparison_key(expression: ExpressionIR) -> tuple[str, str, str] | None:
    if expression.kind != "comparison" or expression.left is None or expression.right is None:
        return None
    left = expression_name(expression.left)
    right = expression_name(expression.right)
    if not left or not right:
        return None
    return left, right, expression.operator


def expression_name(expression: ExpressionIR) -> str:
    if expression.kind == "variable":
        return expression.name
    if expression.kind in {"number", "boolean"}:
        return str(expression.value).lower()
    return ""


def is_complement(first: str, second: str) -> bool:
    return (first, second) in {
        (">=", "<"),
        ("<", ">="),
        (">", "<="),
        ("<=", ">"),
        ("==", "!="),
        ("!=", "=="),
    }


def primary_condition_terms(model: MbdModelIR, expression: ExpressionIR) -> tuple[str, str]:
    variables = expression_variables(expression)
    primary_input = next((name for name in variables if name in model.ports), "")
    primary_parameter = next((name for name in variables if name in model.component.parameters), "")
    return primary_input, primary_parameter


def expression_variables(expression: ExpressionIR) -> list[str]:
    if expression.kind == "variable":
        return [expression.name]
    variables: list[str] = []
    if expression.left is not None:
        variables.extend(expression_variables(expression.left))
    if expression.right is not None:
        variables.extend(expression_variables(expression.right))
    for operand in expression.operands:
        variables.extend(expression_variables(operand))
    return list(dict.fromkeys(variables))


def source_for_signal(flows: list[FlowIR], signal: str) -> str:
    if not signal:
        return ""
    for flow in flows:
        target_signal = flow.target.rsplit(".", 1)[-1]
        source_root = flow.source.split(".", 1)[0]
        if target_signal == signal and source_root != "ScenarioReport":
            return source_root
    return ""


def report_for_signal(flows: list[FlowIR], signal: str) -> str:
    if not signal:
        return ""
    for flow in flows:
        source_signal = flow.source.rsplit(".", 1)[-1]
        if source_signal == signal and flow.target.startswith("ScenarioReport."):
            return flow.target
    return ""


def primary_output_action(model: MbdModelIR, control: ControlRuleIR) -> str:
    for name in control.actions:
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            return name
    return ""
