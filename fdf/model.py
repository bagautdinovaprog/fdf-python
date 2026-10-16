"""Модель данных: точка и карта."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Точка карты высот."""

    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """Двумерная сетка точек."""

    def __init__(self, points: list[list[Point]]) -> None:
        if not points or not points[0]:
            raise ValueError("Карта не может быть пустой")
        self._points = points
        self.height = len(points)
        self.width = len(points[0])

    def __len__(self) -> int:
        """Возвращает общее число точек."""
        return self.width * self.height

    def __iter__(self) -> Iterator[Point]:
        """Обход всех точек в цикле for."""
        for row in self._points:
            yield from row

    def __getitem__(self, xy: tuple[int, int]) -> Point:
        """Получить точку по координатам [x, y]."""
        x, y = xy
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Точка ({x}, {y}) вне карты")
        return self._points[y][x]

    def neighbors(self, x: int, y: int) -> list[Point]:
        """Соседи точки: справа и снизу."""
        result: list[Point] = []
        if x + 1 < self.width:
            result.append(self._points[y][x + 1])
        if y + 1 < self.height:
            result.append(self._points[y + 1][x])
        return result