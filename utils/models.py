from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileOperation:
    name: str
    target_path: Path
    archive_dir: Path
    original_path: Path
