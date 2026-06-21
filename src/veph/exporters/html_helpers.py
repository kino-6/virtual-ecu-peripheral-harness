from __future__ import annotations

from html import escape


def svg_defs(marker_id: str) -> list[str]:
    _ = marker_id
    return [
        "        <defs>",
        '          <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '            <path d="M0,0 L0,6 L9,3 z" fill="#2f5d62"></path>',
        "          </marker>",
        "        </defs>",
    ]


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "..."


def svg_node(title: str, x: int, y: int, note: str) -> list[str]:
    return [
        f'        <rect x="{x}" y="{y}" width="200" height="70" rx="8" class="node"></rect>',
        f'        <text x="{x + 100}" y="{y + 30}" text-anchor="middle" class="node-title">{escape(title)}</text>',
        f'        <text x="{x + 100}" y="{y + 52}" text-anchor="middle" class="node-note">{escape(note)}</text>',
    ]


def ir_svg_node(title: str, x: int, y: int, note: str) -> list[str]:
    return [
        f'        <rect x="{x}" y="{y}" width="230" height="54" rx="8" class="node"></rect>',
        f'        <text x="{x + 115}" y="{y + 22}" text-anchor="middle" class="node-title small">{escape(shorten(title, 34))}</text>',
        f'        <text x="{x + 115}" y="{y + 42}" text-anchor="middle" class="node-note">{escape(note)}</text>',
    ]


def semantic_svg_node(lines: list[str], x: int, y: int, width: int, note: str) -> list[str]:
    center = x + width // 2
    title_lines = lines[:2] or [""]
    if len(title_lines) == 1:
        title_svg = [
            f'        <text x="{center}" y="{y + 30}" text-anchor="middle" class="node-title small">{escape(shorten(title_lines[0], 24))}</text>'
        ]
    else:
        title_svg = [
            f'        <text x="{center}" y="{y + 25}" text-anchor="middle" class="node-title small">{escape(shorten(title_lines[0], 22))}</text>',
            f'        <text x="{center}" y="{y + 43}" text-anchor="middle" class="node-title small">{escape(shorten(title_lines[1], 22))}</text>',
        ]
    return [
        f'        <rect x="{x}" y="{y}" width="{width}" height="70" rx="8" class="node"></rect>',
        *title_svg,
        f'        <text x="{center}" y="{y + 62}" text-anchor="middle" class="node-note">{escape(note)}</text>',
    ]
