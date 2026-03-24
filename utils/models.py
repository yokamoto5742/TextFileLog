from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileOperation:
    name: str
    original_path: Path
    target_path: Path
    archive_dir: Path
