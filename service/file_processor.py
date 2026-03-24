import shutil
from datetime import datetime

from utils.models import FileOperation


class FileProcessor:
    def process(self, op: FileOperation) -> str:
        """ファイルを操作してログメッセージを返す"""
        target = op.target_path
        original = op.original_path

        if not target.exists():
            return f"[スキップ] {op.name}: 指定ファイルが存在しません ({target})"
        if not original.exists():
            return f"[エラー] {op.name}: 原本ファイルが存在しません ({original})"

        if target.stat().st_mtime <= original.stat().st_mtime:
            return f"[スキップ] {op.name}: 指定ファイルは原本から更新されていません"

        dt = datetime.fromtimestamp(target.stat().st_mtime)
        archive_name = f"{target.stem}{dt.strftime('%y%m%d_%H%M%S')}{target.suffix}"
        archive_path = op.archive_dir / archive_name

        try:
            op.archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, archive_path)
            shutil.copy2(original, target)
            return f"[処理済] {op.name}: {target.name} → {archive_path.name} にアーカイブ"
        except Exception as e:
            return f"[エラー] {op.name}: {e}"

    def process_all(self, operations: list[FileOperation]) -> list[str]:
        return [self.process(op) for op in operations]
