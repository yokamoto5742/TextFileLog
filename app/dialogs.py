import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from utils.models import FileOperation

_PAD: dict[str, int] = {"padx": 8, "pady": 4}


class OperationEditDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, operation: FileOperation | None = None):
        super().__init__(parent)
        self.title("ファイル操作の設定")
        self.resizable(False, False)
        self.result: FileOperation | None = None
        self._name_var = tk.StringVar()
        self._original = tk.StringVar()
        self._target = tk.StringVar()
        self._archive = tk.StringVar()
        self._build_ui(operation)
        self.grab_set()
        self.transient(parent)  # type: ignore[arg-type]

    def _build_ui(self, op: FileOperation | None) -> None:
        if op:
            self._name_var.set(op.name)
            self._original.set(str(op.original_path))
            self._target.set(str(op.target_path))
            self._archive.set(str(op.archive_dir))

        tk.Label(self, text="名前:").grid(row=0, column=0, sticky="e", **_PAD)  # type: ignore[arg-type]
        tk.Entry(self, textvariable=self._name_var, width=50).grid(row=0, column=1, columnspan=2, sticky="we", **_PAD)  # type: ignore[arg-type]

        tk.Label(self, text="原本ファイル:").grid(row=1, column=0, sticky="e", **_PAD)  # type: ignore[arg-type]
        tk.Entry(self, textvariable=self._original, width=50).grid(row=1, column=1, sticky="we", **_PAD)  # type: ignore[arg-type]
        tk.Button(self, text="参照", command=self._browse_original).grid(row=1, column=2, **_PAD)  # type: ignore[arg-type]

        tk.Label(self, text="指定ファイル:").grid(row=2, column=0, sticky="e", **_PAD)  # type: ignore[arg-type]
        tk.Entry(self, textvariable=self._target, width=50).grid(row=2, column=1, sticky="we", **_PAD)  # type: ignore[arg-type]
        tk.Button(self, text="参照", command=self._browse_target).grid(row=2, column=2, **_PAD)  # type: ignore[arg-type]

        tk.Label(self, text="アーカイブ先:").grid(row=3, column=0, sticky="e", **_PAD)  # type: ignore[arg-type]
        tk.Entry(self, textvariable=self._archive, width=50).grid(row=3, column=1, sticky="we", **_PAD)  # type: ignore[arg-type]
        tk.Button(self, text="参照", command=self._browse_archive).grid(row=3, column=2, **_PAD)  # type: ignore[arg-type]

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=8)
        tk.Button(btn_frame, text="保存", width=10, command=self._save).pack(side="left", padx=4)
        tk.Button(btn_frame, text="キャンセル", width=10, command=self.destroy).pack(side="left", padx=4)

    def _browse_original(self) -> None:
        path = filedialog.askopenfilename(
            title="原本ファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべて", "*.*")],
        )
        if path:
            self._original.set(path)

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

    def _save(self) -> None:
        name = self._name_var.get().strip()
        original = self._original.get().strip()
        target = self._target.get().strip()
        archive = self._archive.get().strip()

        for label, value in [("名前", name), ("原本ファイル", original), ("指定ファイル", target), ("アーカイブ先", archive)]:
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


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, operations: list[FileOperation]):
        super().__init__(parent)
        self.title("設定")
        self.resizable(True, True)
        self._ops: list[FileOperation] = list(operations)
        self.result: list[FileOperation] | None = None
        self._build_ui()
        self._refresh_list()
        self.grab_set()
        self.transient(parent)  # type: ignore[arg-type]

    def _build_ui(self) -> None:
        tk.Label(self, text="ファイル操作一覧:").pack(anchor="w", padx=8, pady=4)

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self._listbox = tk.Listbox(list_frame, width=50, height=8, yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=4)
        for text, cmd in [("追加", self._add), ("編集", self._edit), ("削除", self._delete)]:
            tk.Button(btn_frame, text=text, width=8, command=cmd).pack(side="left", padx=4)

        bottom = tk.Frame(self)
        bottom.pack(pady=8)
        tk.Button(bottom, text="保存", width=10, command=self._save).pack(side="left", padx=4)
        tk.Button(bottom, text="キャンセル", width=10, command=self.destroy).pack(side="left", padx=4)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        for op in self._ops:
            self._listbox.insert(tk.END, op.name)

    def _selected_index(self, action: str) -> int | None:
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showinfo("選択なし", f"{action}する操作を選択してください", parent=self)
            return None
        return sel[0]

    def _add(self) -> None:
        dlg = OperationEditDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self._ops.append(dlg.result)
            self._refresh_list()

    def _edit(self) -> None:
        idx = self._selected_index("編集")
        if idx is None:
            return
        dlg = OperationEditDialog(self, self._ops[idx])
        self.wait_window(dlg)
        if dlg.result:
            self._ops[idx] = dlg.result
            self._refresh_list()

    def _delete(self) -> None:
        idx = self._selected_index("削除")
        if idx is None:
            return
        if messagebox.askyesno("確認", f"「{self._ops[idx].name}」を削除しますか？", parent=self):
            self._ops.pop(idx)
            self._refresh_list()

    def _save(self) -> None:
        self.result = self._ops
        self.destroy()
