"""Изометрическая проекция и камера."""

import math
from dataclasses import dataclass

from .model import Map, Point

_COS30 = math.cos(math.radians(30))
_SIN30 = math.sin(math.radians(30))


@dataclass(frozen=True)
class ProjectedPoint:
    """Точка на экране."""

    X: float
    Y: float
    color: str | None = None


def project_iso(p: Point, z_scale: float = 1.0) -> tuple[float, float]:
    """Изометрическая проекция одной точки (без масштаба и сдвига)."""
    x_prime = (p.x - p.y) * _COS30
    y_prime = (p.x + p.y) * _SIN30 - p.z * z_scale
    return x_prime, y_prime


@dataclass
class Camera:
    """Камера: масштаб, сдвиг, параметры проекции."""

    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_scale: float = 1.0
    angle: float = math.radians(30)
    top_view: bool = False

    def _project_raw(self, p: Point) -> tuple[float, float]:
        if self.top_view:
            return float(p.x), float(p.y)
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        x_prime = (p.x - p.y) * cos_a
        y_prime = (p.x + p.y) * sin_a - p.z * self.z_scale
        return x_prime, y_prime

    def project(self, p: Point) -> ProjectedPoint:
        """Полная проекция с масштабом и сдвигом."""
        x_prime, y_prime = self._project_raw(p)
        return ProjectedPoint(
            X=x_prime * self.scale + self.offset_x,
            Y=y_prime * self.scale + self.offset_y,
            color=p.color,
        )

    def fit(self, m: Map, width: int, height: int) -> None:
        """Подгоняет масштаб и сдвиг под размер окна."""
        xs: list[float] = []
        ys: list[float] = []
        for p in m:
            xp, yp = self._project_raw(p)
            xs.append(xp)
            ys.append(yp)

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        bbox_w = max_x - min_x
        bbox_h = max_y - min_y

        if bbox_w < 1e-9:
            bbox_w = 1.0
        if bbox_h < 1e-9:
            bbox_h = 1.0

        self.scale = min(width / bbox_w, height / bbox_h) * 0.9

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.offset_x = width / 2 - center_x * self.scale
        self.offset_y = height / 2 - center_y * self.scale


def lerp_color(a: str, b: str, t: float) -> str:
    """Интерполяция между двумя цветами #RRGGBB."""
    t = max(0.0, min(1.0, t))
    ra, ga, ba = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    rb, gb, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    r = int(ra + (rb - ra) * t)
    g = int(ga + (gb - ga) * t)
    blue = int(ba + (bb - ba) * t)
    return f"#{r:02X}{g:02X}{blue:02X}"


def height_color(z: int, z_min: int, z_max: int) -> str:
    """Цвет по высоте: синий → зелёный → жёлтый → красный."""
    if z_max == z_min:
        return "#00FF00"
    t = (z - z_min) / (z_max - z_min)
    palette = ["#0000FF", "#00FF00", "#FFFF00", "#FF0000"]
    seg = t * (len(palette) - 1)
    i = int(seg)
    if i >= len(palette) - 1:
        return palette[-1]
    local_t = seg - i
    return lerp_color(palette[i], palette[i + 1], local_t)