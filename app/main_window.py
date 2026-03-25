import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from app import __version__
from app.settings_dialog import SettingsDialog
from service.file_processor import FileProcessor
from service.startup_manager import TaskSchedulerManager
from utils.config_manager import ConfigManager
from utils.models import FileOperation


class MainApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"TextFileLog v{__version__}")
        self.resizable(True, True)

        self._config = ConfigManager()
        self._processor = FileProcessor()
        self._scheduler = TaskSchedulerManager()
        self._operations: list[FileOperation] = self._config.load()

        self._build_ui()
        self._refresh_list()
        self._update_task_button()

    def _build_ui(self) -> None:
        tk.Label(self, text="ファイル操作一覧:").pack(anchor="w", padx=8, pady=4)

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self._listbox = tk.Listbox(list_frame, width=60, height=6, yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        btn_frame = tk.Frame(self)
        btn_frame.pack(anchor="w", pady=4, padx=8)
        tk.Button(btn_frame, text="実行", width=10, command=self._run).pack(side="left", padx=4)
        tk.Button(btn_frame, text="設定", width=10, command=self._open_settings).pack(side="left", padx=4)
        self._task_btn = tk.Button(btn_frame, text="自動実行登録", width=12, command=self._toggle_task)
        self._task_btn.pack(side="left", padx=4)
        tk.Button(btn_frame, text="閉じる", width=10, command=self.destroy).pack(side="left", padx=4)

        tk.Label(self, text="ログ:").pack(anchor="w", padx=8, pady=4)
        self._log = ScrolledText(self, height=10, state="disabled", wrap="word")
        self._log.pack(fill="both", expand=True, padx=8, pady=4)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        for op in self._operations:
            self._listbox.insert(tk.END, op.name)

    def _update_task_button(self) -> None:
        text = "自動実行解除" if self._scheduler.is_registered() else "自動実行登録"
        self._task_btn.config(text=text)

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.config(state="normal")
        self._log.insert(tk.END, f"[{timestamp}] {message}\n")
        self._log.see(tk.END)
        self._log.config(state="disabled")

    def _run(self) -> None:
        if not self._operations:
            messagebox.showinfo("ファイル操作なし", "ファイル操作が設定されていません。\n設定ボタンから追加してください。")
            return
        for msg in self._processor.process_all(self._operations):
            self._append_log(msg)

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
            _, msg = self._scheduler.unregister()
        else:
            _, msg = self._scheduler.register()
        self._update_task_button()
        self._append_log(msg)
