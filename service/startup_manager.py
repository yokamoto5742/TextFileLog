import sys
import winreg
from pathlib import Path

TASK_NAME = "TextFileLog"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _build_startup_command() -> str:
    script_path = Path(sys.argv[0]).resolve()
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --auto'
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    if not pythonw.exists():
        pythonw = Path(sys.executable)
    return f'"{pythonw}" "{script_path}" --auto'


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
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, _RUN_KEY, access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.SetValueEx(key, TASK_NAME, 0, winreg.REG_SZ, _build_startup_command())
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
