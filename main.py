"""Точка входа программы FdF."""

import sys

from fdf.app import App
from fdf.errors import FdfError, MapFormatError
from fdf.parser import parse


def main() -> int:
    if len(sys.argv) != 2:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        return 2

    path = sys.argv[1]

    try:
        m = parse(path)
    except FileNotFoundError:
        print(f"Файл не найден: {path}", file=sys.stderr)
        return 1
    except MapFormatError as e:
        print(f"Ошибка формата: {e}", file=sys.stderr)
        return 1
    except FdfError as e:
        print(f"Ошибка FdF: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Ошибка чтения: {e}", file=sys.stderr)
        return 1

    App(m).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())