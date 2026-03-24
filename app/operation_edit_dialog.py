import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

from utils.models import FileOperation

_PAD: dict[str, Any] = {"padx": 8, "pady": 4}


class OperationEditDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, operation: FileOperation | None = None):
        super().__init__(parent)
        self.title("ファイル操作設定")
        self.resizable(False, False)
        self.result: FileOperation | None = None
        self._name_var = tk.StringVar()
        self._original = tk.StringVar()
        self._target = tk.StringVar()
        self._archive = tk.StringVar()
        self._build_ui(operation)
        self.grab_set()
        self.transient(parent)  # type: ignore[arg-type, reportCallIssue]

    def _build_ui(self, op: FileOperation | None) -> None:
        if op:
            self._name_var.set(op.name)
            self._original.set(str(op.original_path))
            self._target.set(str(op.target_path))
            self._archive.set(str(op.archive_dir))

        tk.Label(self, text="名称:").grid(row=0, column=0, sticky="e", **_PAD)
        tk.Entry(self, textvariable=self._name_var, width=50).grid(row=0, column=1, columnspan=2, sticky="we", **_PAD)

        tk.Label(self, text="指定ファイル:").grid(row=2, column=0, sticky="e", **_PAD)
        tk.Entry(self, textvariable=self._target, width=50).grid(row=2, column=1, sticky="we", **_PAD)
        tk.Button(self, text="参照", command=self._browse_target).grid(row=2, column=2, **_PAD)

        tk.Label(self, text="アーカイブ先:").grid(row=3, column=0, sticky="e", **_PAD)
        tk.Entry(self, textvariable=self._archive, width=50).grid(row=3, column=1, sticky="we", **_PAD)
        tk.Button(self, text="参照", command=self._browse_archive).grid(row=3, column=2, **_PAD)

        tk.Label(self, text="原本ファイル:").grid(row=1, column=0, sticky="e", **_PAD)
        tk.Entry(self, textvariable=self._original, width=50).grid(row=1, column=1, sticky="we", **_PAD)
        tk.Button(self, text="参照", command=self._browse_original).grid(row=1, column=2, **_PAD)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=8, sticky="w")
        tk.Button(btn_frame, text="保存", width=10, command=self._save).pack(side="left", padx=4)
        tk.Button(btn_frame, text="キャンセル", width=10, command=self.destroy).pack(side="left", padx=4)

    def _browse_target(self) -> None:
        path = filedialog.askopenfilename(
            title="指定ファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべて", "*.*")],
        )
        if path:
            self._target.set(path)

    def _browse_archive(self) -> None:
        path = filedialog.askdirectory(title="アーカイブ先ディレクトリを選択")
        if path:
            self._archive.set(path)

    def _browse_original(self) -> None:
        path = filedialog.askopenfilename(
            title="原本ファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべて", "*.*")],
        )
        if path:
            self._original.set(path)

    def _save(self) -> None:
        name = self._name_var.get().strip()
        original = self._original.get().strip()
        target = self._target.get().strip()
        archive = self._archive.get().strip()

        for label, value in [("名称", name), ("指定ファイル", target), ("アーカイブ先", archive),("原本ファイル", original)]:
            if not value:
                messagebox.showwarning("入力エラー", f"{label}を入力してください", parent=self)
                return

        self.result = FileOperation(
            name=name,
            original_path=Path(original),
            target_path=Path(target),
            archive_dir=Path(archive),
        )
        self.destroy()

