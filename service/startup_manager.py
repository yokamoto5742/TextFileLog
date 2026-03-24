import sys
import winreg
from pathlib import Path

from utils.config_manager import ConfigManager


def _build_startup_command() -> str:
    script_path = Path(sys.argv[0]).resolve()
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --auto'
    # Python環境での設定
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    if not pythonw.exists():
        pythonw = Path(sys.executable)
    return f'"{pythonw}" "{script_path}" --auto'


class TaskSchedulerManager:
    def __init__(self) -> None:
        task_name, run_key = ConfigManager().load_startup()
        self._task_name = task_name
        self._run_key = run_key

    def is_registered(self) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._run_key) as key:
                winreg.QueryValueEx(key, self._task_name)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def register(self) -> tuple[bool, str]:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, self._run_key, access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.SetValueEx(key, self._task_name, 0, winreg.REG_SZ, _build_startup_command())
            return True, "スタートアップに登録しました"
        except Exception as e:
            return False, f"登録失敗: {e}"

    def unregister(self) -> tuple[bool, str]:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, self._run_key, access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.DeleteValue(key, self._task_name)
            return True, "スタートアップから削除しました"
        except FileNotFoundError:
            return True, "スタートアップから削除しました"
        except Exception as e:
            return False, f"削除失敗: {e}"
