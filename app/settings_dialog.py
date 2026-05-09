import tkinter as tk
from tkinter import messagebox

from utils.models import FileOperation

from app.operation_edit_dialog import OperationEditDialog


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, operations: list[FileOperation], on_delete=None):
        super().__init__(parent)
        self.title("設定")
        self.resizable(True, True)
        self._ops: list[FileOperation] = list(operations)
        self.result: list[FileOperation] | None = None
        self._on_delete = on_delete
        self._build_ui()
        self._refresh_list()
        self.grab_set()
        self.transient(parent)  # type: ignore[arg-type, reportCallIssue]

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
        btn_frame.pack(anchor="w", pady=4, padx=8)
        for text, cmd in [("追加", self._add), ("編集", self._edit), ("削除", self._delete)]:
            tk.Button(btn_frame, text=text, width=8, command=cmd).pack(side="left", padx=4)

        bottom = tk.Frame(self)
        bottom.pack(anchor="w", pady=8, padx=8)
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
            if self._on_delete:
                self._on_delete(list(self._ops))

    def _save(self) -> None:
        self.result = self._ops
        self.destroy()
