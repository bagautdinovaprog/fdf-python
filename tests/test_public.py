import tempfile
from pathlib import Path

import pytest

from fdf.errors import MapFormatError
from fdf.model import Point
from fdf.parser import parse
from fdf.projection import Camera, height_color, lerp_color, project_iso


def test_parse_elem():
    m = parse("maps/elem.fdf")
    assert m.width == 5
    assert m.height == 5
    center = m[2, 2]
    assert center.z == 5


@pytest.mark.parametrize("token, expected_z, expected_color", [
    ("7", 7, None),
    ("-3", -3, None),
    ("2,0xFF8800", 2, "#FF8800"),
    ("1,0xff", 1, "#0000FF"),
])
def test_parse_tokens(token, expected_z, expected_color):
    with tempfile.NamedTemporaryFile("w", suffix=".fdf", delete=False) as f:
        f.write(token)
        path = Path(f.name)
    try:
        m = parse(path)
        p = m[0, 0]
        assert p.z == expected_z
        assert p.color == expected_color
    finally:
        path.unlink()


@pytest.mark.parametrize("bad_file", [
    "maps/bad/empty.fdf",
    "maps/bad/not_a_number.fdf",
    "maps/bad/different_lengths.fdf",
    "maps/bad/bad_color.fdf",
])
def test_bad_maps(bad_file):
    with pytest.raises(MapFormatError):
        parse(bad_file)


def test_project_iso_origin():
    x, y = project_iso(Point(0, 0, 0))
    assert x == 0.0 and y == 0.0


def test_project_iso_height():
    _, y = project_iso(Point(0, 0, 1), z_scale=1.0)
    assert y < 0


def test_camera_fit():
    m = parse("maps/elem.fdf")
    cam = Camera()
    cam.fit(m, 800, 600)
    xs, ys = [], []
    for p in m:
        pr = cam.project(p)
        xs.append(pr.X)
        ys.append(pr.Y)
    assert min(xs) >= 0 and max(xs) <= 800
    assert min(ys) >= 0 and max(ys) <= 600


def test_map_len():
    m = parse("maps/elem.fdf")
    assert len(m) == 25


def test_neighbors():
    m = parse("maps/elem.fdf")
    n = m.neighbors(0, 0)
    assert len(n) == 2


def test_lerp_color():
    assert lerp_color("#000000", "#FFFFFF", 0.5) == "#7F7F7F"


def test_height_color():
    c = height_color(5, 0, 10)
    assert c.startswith("#") and len(c) == 7