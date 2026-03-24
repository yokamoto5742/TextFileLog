import configparser
import sys
from pathlib import Path

from utils.models import FileOperation


def _get_config_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return base / "config.ini"


CONFIG_PATH: Path = _get_config_path()


class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path

    def _read(self) -> configparser.ConfigParser:
        cp = configparser.ConfigParser()
        if self.path.exists():
            cp.read(self.path, encoding="utf-8")
        return cp

    def load(self) -> list[FileOperation]:
        cp = self._read()
        ops: list[FileOperation] = []
        for section in cp.sections():
            if not section.startswith("operation_"):
                continue
            try:
                op = FileOperation(
                    name=cp.get(section, "name", fallback=section),
                    original_path=Path(cp.get(section, "original_path")),
                    target_path=Path(cp.get(section, "target_path")),
                    archive_dir=Path(cp.get(section, "archive_dir")),
                )
                ops.append(op)
            except (configparser.NoOptionError, Exception):
                pass
        return ops

    def save(self, operations: list[FileOperation]) -> None:
        cp = self._read()
        for section in cp.sections():
            if section.startswith("operation_"):
                cp.remove_section(section)
        for i, op in enumerate(operations, start=1):
            section = f"operation_{i}"
            cp.add_section(section)
            cp.set(section, "name", op.name)
            cp.set(section, "original_path", str(op.original_path))
            cp.set(section, "target_path", str(op.target_path))
            cp.set(section, "archive_dir", str(op.archive_dir))
        with self.path.open("w", encoding="utf-8") as f:
            cp.write(f)
