"""Ошибки программы FdF."""


class FdfError(Exception):
    """Базовая ошибка FdF."""


class MapFormatError(FdfError):
    """Ошибка формата карты высот."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        self.line = line
        self.column = column
        if line is not None and column is not None:
            full = f"строка {line}, колонка {column}: {message}"
        else:
            full = message
        super().__init__(full)