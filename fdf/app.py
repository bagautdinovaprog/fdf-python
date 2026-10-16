"""Графический интерфейс на tkinter."""

import tkinter as tk

from .model import Map, Point
from .projection import Camera, ProjectedPoint


class App:
    """Главное окно приложения."""

    DEFAULT_COLOR = "#FFFFFF"

    def __init__(self, m: Map) -> None:
        self.map = m
        self.camera = Camera()

        self.root = tk.Tk()
        self.root.title("FdF — каркасная 3D-модель")
        self.root.geometry("900x700")

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.bind("<Configure>", lambda e: self._redraw())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Бонусы: колесо мыши, стрелки, +/-
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.root.bind("<Up>", lambda e: self._move(0, -20))
        self.root.bind("<Down>", lambda e: self._move(0, 20))
        self.root.bind("<Left>", lambda e: self._move(-20, 0))
        self.root.bind("<Right>", lambda e: self._move(20, 0))
        self.root.bind("<plus>", lambda e: self._change_z(1))
        self.root.bind("<equal>", lambda e: self._change_z(1))
        self.root.bind("<minus>", lambda e: self._change_z(-1))
        self.root.bind("<t>", lambda e: self._toggle_top())

        self._redraw()

    def _redraw(self) -> None:
        w = self.canvas.winfo_width() or 900
        h = self.canvas.winfo_height() or 700
        self.camera.fit(self.map, w, h)
        self.canvas.delete("all")

        # Находим min/max z для цвета по высоте
        zs = [p.z for p in self.map]
        z_min, z_max = min(zs), max(zs)

        for p in self.map:
            a = self.camera.project(p)
            for n in self.map.neighbors(p.x, p.y):
                b = self.camera.project(n)
                color = self._edge_color(p, n, a, b, z_min, z_max)
                self.canvas.create_line(a.X, a.Y, b.X, b.Y, fill=color)

    def _edge_color(
    self,
    p1: Point,
    p2: Point,
    a: ProjectedPoint,
    b: ProjectedPoint,
    z_min: int,
    z_max: int,
) -> str:
        """Цвет ребра: если у концов есть цвет — берём их, иначе по высоте."""
        from .projection import height_color, lerp_color

        c1 = p1.color or height_color(p1.z, z_min, z_max)
        c2 = p2.color or height_color(p2.z, z_min, z_max)
        return lerp_color(c1, c2, 0.5)

    # --- бонусные обработчики ---
    def _on_zoom(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 1 / 1.1
        cx, cy = event.x, event.y
        self.camera.offset_x = cx - (cx - self.camera.offset_x) * factor
        self.camera.offset_y = cy - (cy - self.camera.offset_y) * factor
        self.camera.scale *= factor
        self.canvas.delete("all")
        self._redraw_static()

    def _move(self, dx: int, dy: int) -> None:
        self.camera.offset_x += dx
        self.camera.offset_y += dy
        self.canvas.delete("all")
        self._redraw_static()

    def _change_z(self, delta: float) -> None:
        self.camera.z_scale = max(0.1, self.camera.z_scale + delta)
        self.canvas.delete("all")
        self._redraw_static()

    def _toggle_top(self) -> None:
        self.camera.top_view = not self.camera.top_view
        self.canvas.delete("all")
        self._redraw_static()

    def _redraw_static(self) -> None:
        """Перерисовка без fit (чтобы не сбрасывать ручной зум)."""
        zs = [p.z for p in self.map]
        z_min, z_max = min(zs), max(zs)
        for p in self.map:
            a = self.camera.project(p)
            for n in self.map.neighbors(p.x, p.y):
                b = self.camera.project(n)
                color = self._edge_color(p, n, a, b, z_min, z_max)
                self.canvas.create_line(a.X, a.Y, b.X, b.Y, fill=color)

    def run(self) -> None:
        self.root.mainloop()