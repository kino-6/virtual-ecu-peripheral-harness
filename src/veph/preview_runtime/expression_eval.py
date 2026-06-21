from __future__ import annotations

import ast
import operator
from typing import Any

from veph.ir import ExpressionIR
from veph.preview_runtime.errors import PreviewScenarioError


def expression_is_true(expression: ExpressionIR, context: dict[str, Any]) -> bool:
    return bool(expression_value(expression, context))


def expression_value(expression: ExpressionIR, context: dict[str, Any]) -> Any:
    if expression.kind == "always":
        return True
    if expression.kind == "variable":
        return resolve_value(expression.name, context)
    if expression.kind in {"number", "boolean"}:
        return expression.value
    if expression.kind == "comparison":
        if expression.left is None or expression.right is None:
            raise PreviewScenarioError(f"unsupported condition: {expression.source}")
        return compare_values(
            expression_value(expression.left, context),
            expression.operator,
            expression_value(expression.right, context),
        )
    if expression.kind == "logical":
        if expression.operator == "and":
            return all(expression_is_true(operand, context) for operand in expression.operands)
        if expression.operator == "or":
            return any(expression_is_true(operand, context) for operand in expression.operands)
        if expression.operator == "not":
            if len(expression.operands) != 1:
                raise PreviewScenarioError(f"unsupported condition: {expression.source}")
            return not expression_is_true(expression.operands[0], context)
    raise PreviewScenarioError(
        f"unsupported condition: {expression.source or expression.diagnostic or expression.kind}"
    )


def compare_values(left_value: Any, op_text: str, right_value: Any) -> bool:
    ops = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne,
    }
    if op_text not in ops:
        raise PreviewScenarioError(f"unsupported operator: {op_text}")
    return bool(ops[op_text](left_value, right_value))


def resolve_value(token: str, context: dict[str, Any]) -> Any:
    if token in context:
        return context[token]
    if any(operator_text in token for operator_text in ["+", "-", "*", "/", "(", ")"]):
        try:
            return _evaluate_arithmetic_expression(token, context)
        except PreviewScenarioError:
            raise
        except Exception:
            pass
    return coerce_value(token)


def coerce_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            number = float(value)
        except ValueError:
            return value
        if number.is_integer():
            return int(number)
        return number
    return value


def _evaluate_arithmetic_expression(text: str, context: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise PreviewScenarioError(f"unsupported arithmetic expression: {text}") from exc
    return _evaluate_arithmetic_node(tree.body, context)


def _evaluate_arithmetic_node(node: ast.AST, context: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in context:
            raise PreviewScenarioError(f"unknown arithmetic signal: {node.id}")
        return context[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_arithmetic_node(node.operand, context)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        op = operations.get(type(node.op))
        if op is None:
            raise PreviewScenarioError("unsupported arithmetic operator")
        left = _require_number(_evaluate_arithmetic_node(node.left, context))
        right = _require_number(_evaluate_arithmetic_node(node.right, context))
        return op(left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        args = [_evaluate_arithmetic_node(arg, context) for arg in node.args]
        if node.func.id == "clamp" and len(args) == 3:
            value, lower, upper = (_require_number(arg) for arg in args)
            return min(max(value, lower), upper)
        if node.func.id == "lookup1d" and len(args) == 2:
            return _lookup1d(_require_number(args[0]), _table_points(args[1]))
    raise PreviewScenarioError("unsupported arithmetic expression")


def _require_number(value: Any) -> int | float:
    if isinstance(value, (int, float)):
        return value
    raise PreviewScenarioError(f"non-numeric arithmetic value: {value!r}")


def _table_points(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, str):
        raise PreviewScenarioError("lookup1d table points must be a string parameter")
    points: list[tuple[float, float]] = []
    for item in value.split(","):
        left, separator, right = item.strip().partition(":")
        if not separator:
            left, separator, right = item.strip().partition("=")
        if not separator:
            raise PreviewScenarioError(f"invalid lookup1d table point: {item}")
        points.append((float(left), float(right)))
    if len(points) < 2:
        raise PreviewScenarioError("lookup1d requires at least two table points")
    return sorted(points)


def _lookup1d(value: int | float, points: list[tuple[float, float]]) -> int | float:
    if value <= points[0][0]:
        return _coerce_number(points[0][1])
    if value >= points[-1][0]:
        return _coerce_number(points[-1][1])
    for (left_x, left_y), (right_x, right_y) in zip(points, points[1:]):
        if left_x <= value <= right_x:
            ratio = (value - left_x) / (right_x - left_x)
            return _coerce_number(left_y + ratio * (right_y - left_y))
    return _coerce_number(points[-1][1])


def _coerce_number(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value
