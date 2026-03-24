import configparser
import shutil
import sys
import tkinter as tk
import winreg
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
CONFIG_PATH = Path(__file__).parent / "utils/config.ini"
TASK_NAME = "TextFileLog"
SCRIPT_PATH = Path(__file__).resolve()


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------
@dataclass
class FileOperation:
    name: str
    original_path: Path
    target_path: Path
    archive_dir: Path


# ---------------------------------------------------------------------------
# ConfigManager
# ---------------------------------------------------------------------------
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

        # 既存の operation_* セクションを削除
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



# ---------------------------------------------------------------------------
# FileProcessor
# ---------------------------------------------------------------------------
class FileProcessor:
    def process(self, op: FileOperation) -> str:
        """1件のファイル操作を処理してログメッセージを返す。"""
        target = op.target_path
        original = op.original_path

        if not target.exists():
            return f"[スキップ] {op.name}: 指定ファイルが存在しません ({target})"
        if not original.exists():
            return f"[エラー] {op.name}: 原本ファイルが存在しません ({original})"

        target_mtime = target.stat().st_mtime
        original_mtime = original.stat().st_mtime

        if target_mtime <= original_mtime:
            return f"[スキップ] {op.name}: 指定ファイルは原本から更新されていません"

        # アーカイブファイル名: {指定ファイルのstem}{yymmdd_hhmmss}{suffix}
        dt = datetime.fromtimestamp(target_mtime)
        timestamp = dt.strftime("%y%m%d_%H%M%S")
        archive_name = f"{target.stem}{timestamp}{target.suffix}"
        archive_path = op.archive_dir / archive_name

        try:
            op.archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, archive_path)
            shutil.copy2(original, target)
            return (
                f"[処理済] {op.name}: "
                f"{target.name} → {archive_path.name} にアーカイブ、原本で上書き"
            )
        except Exception as e:
            return f"[エラー] {op.name}: {e}"

    def process_all(self, operations: list[FileOperation]) -> list[str]:
        return [self.process(op) for op in operations]


# ---------------------------------------------------------------------------
# TaskSchedulerManager
# ---------------------------------------------------------------------------
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


class TaskSchedulerManager:
    def is_registered(self) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
                winreg.QueryValueEx(key, TASK_NAME)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def register(self) -> tuple[bool, str]:
        pythonw = Path(sys.executable).parent / "pythonw.exe"
        if not pythonw.exists():
            pythonw = Path(sys.executable)

        cmd = f'"{pythonw}" "{SCRIPT_PATH}" --auto'
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, _RUN_KEY, access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.SetValueEx(key, TASK_NAME, 0, winreg.REG_SZ, cmd)
            return True, "スタートアップに登録しました"
        except Exception as e:
            return False, f"登録失敗: {e}"

    def unregister(self) -> tuple[bool, str]:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, _RUN_KEY, access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.DeleteValue(key, TASK_NAME)
            return True, "スタートアップから削除しました"
        except FileNotFoundError:
            return True, "スタートアップから削除しました"
        except Exception as e:
            return False, f"削除失敗: {e}"


# ---------------------------------------------------------------------------
# OperationEditDialog — 1件の操作を追加・編集するダイアログ
# ---------------------------------------------------------------------------
class OperationEditDialog(tk.Toplevel):
    def __init__(self, parent, operation: FileOperation | None = None):
        super().__init__(parent)
        self.title("ファイル操作の設定")
        self.resizable(False, False)
        self.result: FileOperation | None = None

        self._build_ui(operation)
        self.grab_set()
        self.transient(parent)

    def _build_ui(self, op: FileOperation | None) -> None:
        pad = {"padx": 8, "pady": 4}

        # 名前
        tk.Label(self, text="名前:").grid(row=0, column=0, sticky="e", **pad)
        self._name_var = tk.StringVar(value=op.name if op else "")
        tk.Entry(self, textvariable=self._name_var, width=50).grid(row=0, column=1, columnspan=2, sticky="we", **pad)

        # 原本ファイル
        tk.Label(self, text="原本ファイル:").grid(row=1, column=0, sticky="e", **pad)
        self._original = tk.StringVar(value=str(op.original_path) if op else "")
        tk.Entry(self, textvariable=self._original, width=50).grid(row=1, column=1, sticky="we", **pad)
        tk.Button(self, text="参照", command=self._browse_original).grid(row=1, column=2, **pad)

        # 指定ファイル
        tk.Label(self, text="指定ファイル:").grid(row=2, column=0, sticky="e", **pad)
        self._target = tk.StringVar(value=str(op.target_path) if op else "")
        tk.Entry(self, textvariable=self._target, width=50).grid(row=2, column=1, sticky="we", **pad)
        tk.Button(self, text="参照", command=self._browse_target).grid(row=2, column=2, **pad)

        # アーカイブディレクトリ
        tk.Label(self, text="アーカイブ先:").grid(row=3, column=0, sticky="e", **pad)
        self._archive = tk.StringVar(value=str(op.archive_dir) if op else "")
        tk.Entry(self, textvariable=self._archive, width=50).grid(row=3, column=1, sticky="we", **pad)
        tk.Button(self, text="参照", command=self._browse_archive).grid(row=3, column=2, **pad)

        # ボタン行
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

        if not name:
            messagebox.showwarning("入力エラー", "名前を入力してください", parent=self)
            return
        if not original:
            messagebox.showwarning("入力エラー", "原本ファイルを指定してください", parent=self)
            return
        if not target:
            messagebox.showwarning("入力エラー", "指定ファイルを指定してください", parent=self)
            return
        if not archive:
            messagebox.showwarning("入力エラー", "アーカイブ先を指定してください", parent=self)
            return

        self.result = FileOperation(
            name=name,
            original_path=Path(original),
            target_path=Path(target),
            archive_dir=Path(archive),
        )
        self.destroy()


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, operations: list[FileOperation]):
        super().__init__(parent)
        self.title("設定")
        self.resizable(True, True)
        self._ops: list[FileOperation] = list(operations)
        self.result: list[FileOperation] | None = None

        self._build_ui()
        self._refresh_list()
        self.grab_set()
        self.transient(parent)

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        tk.Label(self, text="ファイル操作一覧:").pack(anchor="w", **pad)

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self._listbox = tk.Listbox(list_frame, width=50, height=8, yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=4)
        tk.Button(btn_frame, text="追加", width=8, command=self._add).pack(side="left", padx=4)
        tk.Button(btn_frame, text="編集", width=8, command=self._edit).pack(side="left", padx=4)
        tk.Button(btn_frame, text="削除", width=8, command=self._delete).pack(side="left", padx=4)

        bottom = tk.Frame(self)
        bottom.pack(pady=8)
        tk.Button(bottom, text="保存", width=10, command=self._save).pack(side="left", padx=4)
        tk.Button(bottom, text="キャンセル", width=10, command=self.destroy).pack(side="left", padx=4)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        for op in self._ops:
            self._listbox.insert(tk.END, op.name)

    def _add(self) -> None:
        dlg = OperationEditDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self._ops.append(dlg.result)
            self._refresh_list()

    def _edit(self) -> None:
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showinfo("選択なし", "編集する操作を選択してください", parent=self)
            return
        idx = sel[0]
        dlg = OperationEditDialog(self, self._ops[idx])
        self.wait_window(dlg)
        if dlg.result:
            self._ops[idx] = dlg.result
            self._refresh_list()

    def _delete(self) -> None:
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showinfo("選択なし", "削除する操作を選択してください", parent=self)
            return
        idx = sel[0]
        name = self._ops[idx].name
        if messagebox.askyesno("確認", f"「{name}」を削除しますか？", parent=self):
            self._ops.pop(idx)
            self._refresh_list()

    def _save(self) -> None:
        self.result = self._ops
        self.destroy()


# ---------------------------------------------------------------------------
# MainApp
# ---------------------------------------------------------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TextFileLog")
        self.resizable(True, True)

        self._config = ConfigManager()
        self._processor = FileProcessor()
        self._scheduler = TaskSchedulerManager()
        self._operations: list[FileOperation] = self._config.load()

        self._build_ui()
        self._refresh_list()
        self._update_task_button()

        # 起動時に前回実行日チェックして自動実行
        self.after(100, self._auto_run_on_start)

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        tk.Label(self, text="ファイル操作一覧:").pack(anchor="w", **pad)

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self._listbox = tk.Listbox(list_frame, width=60, height=6, yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=4)

        tk.Button(btn_frame, text="実行", width=10, command=self._run).pack(side="left", padx=4)
        tk.Button(btn_frame, text="設定", width=10, command=self._open_settings).pack(side="left", padx=4)
        self._task_btn = tk.Button(btn_frame, text="タスク登録", width=12, command=self._toggle_task)
        self._task_btn.pack(side="left", padx=4)

        tk.Label(self, text="ログ:").pack(anchor="w", **pad)

        self._log = ScrolledText(self, height=10, state="disabled", wrap="word")
        self._log.pack(fill="both", expand=True, padx=8, pady=4)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        for op in self._operations:
            self._listbox.insert(tk.END, op.name)

    def _update_task_button(self) -> None:
        if self._scheduler.is_registered():
            self._task_btn.config(text="タスク解除")
        else:
            self._task_btn.config(text="タスク登録")

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.config(state="normal")
        self._log.insert(tk.END, f"[{timestamp}] {message}\n")
        self._log.see(tk.END)
        self._log.config(state="disabled")

    def _run(self) -> None:
        if not self._operations:
            messagebox.showinfo("操作なし", "ファイル操作が設定されていません。\n設定ボタンから追加してください。")
            return
        results = self._processor.process_all(self._operations)
        for msg in results:
            self._append_log(msg)

    def _auto_run_on_start(self) -> None:
        if self._operations:
            self._append_log("起動時の自動実行を開始します")
            self._run()

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self, self._operations)
        self.wait_window(dlg)
        if dlg.result is not None:
            self._operations = dlg.result
            self._config.save(self._operations)
            self._refresh_list()
            self._append_log("設定を保存しました")

    def _toggle_task(self) -> None:
        if self._scheduler.is_registered():
            ok, msg = self._scheduler.unregister()
        else:
            ok, msg = self._scheduler.register()

        if ok:
            messagebox.showinfo("タスクスケジューラ", msg)
        else:
            messagebox.showerror("タスクスケジューラ", msg)
        self._update_task_button()
        self._append_log(msg)


# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------
def run_auto() -> None:
    """--auto モード: GUIなしで処理して終了"""
    config = ConfigManager()
    operations = config.load()
    if not operations:
        return

    processor = FileProcessor()
    processor.process_all(operations)


def main() -> None:
    if "--auto" in sys.argv:
        run_auto()
    else:
        app = MainApp()
        app.mainloop()


if __name__ == "__main__":
    main()
