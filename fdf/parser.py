"""Парсер файлов .fdf."""

import re
from pathlib import Path

from .errors import MapFormatError
from .model import Map, Point

# Регулярка: число, потом опционально запятая и цвет 0x...
_VALUE_RE = re.compile(r"^(?P<z>-?\d+)(?:,(?P<color>0x[0-9a-fA-F]{1,6}))?$")


def _parse_color(raw: str) -> str:
    """Превращает '0xff' в '#0000FF'."""
    hex_part = raw[2:].upper()
    hex_part = hex_part.zfill(6)
    return f"#{hex_part}"


def _parse_token(token: str, line: int, column: int) -> tuple[int, str | None]:
    """Разбирает одно значение типа '5' или '2,0xFF0000'."""
    match = _VALUE_RE.match(token)
    if match is None:
        raise MapFormatError(f"'{token}' — некорректное значение", line, column)
    z = int(match.group("z"))
    color_raw = match.group("color")
    color = _parse_color(color_raw) if color_raw is not None else None
    return z, color


def parse(path: str | Path) -> Map:
    """Читает файл .fdf и возвращает Map."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    points: list[list[Point]] = []
    width: int | None = None

    for line_idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            if points:
                raise MapFormatError("пустая строка внутри карты", line_idx, 1)
            continue

        tokens = stripped.split()
        if width is None:
            width = len(tokens)
        elif len(tokens) != width:
            raise MapFormatError(
                f"длина строки {len(tokens)}, ожидалось {width}",
                line_idx,
                1,
            )

        row: list[Point] = []
        for col_idx, token in enumerate(tokens, start=1):
            z, color = _parse_token(token, line_idx, col_idx)
            row.append(Point(x=col_idx - 1, y=line_idx - 1, z=z, color=color))
        points.append(row)

    if not points or width is None or width == 0:
        raise MapFormatError("карта пуста", 1, 1)

    return Map(points)