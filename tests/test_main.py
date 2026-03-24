from unittest.mock import MagicMock, patch

from main import run_auto


def test_run_auto_calls_config_load():
    """起動時に ConfigManager.load() を呼ぶ"""
    with patch("main.ConfigManager") as mock_cm, patch("main.FileProcessor"):
        mock_cm.return_value.load.return_value = []
        run_auto()
        mock_cm.return_value.load.assert_called_once()


def test_run_auto_no_operations_skips_processing():
    """操作が 0 件のとき process_all を呼ばない"""
    with patch("main.ConfigManager") as mock_cm, patch("main.FileProcessor") as mock_fp:
        mock_cm.return_value.load.return_value = []
        run_auto()
        mock_fp.return_value.process_all.assert_not_called()


def test_run_auto_with_operations_calls_process_all():
    """操作が 1 件以上あるとき process_all に渡す"""
    with patch("main.ConfigManager") as mock_cm, patch("main.FileProcessor") as mock_fp:
        operations = [MagicMock(), MagicMock()]
        mock_cm.return_value.load.return_value = operations
        run_auto()
        mock_fp.return_value.process_all.assert_called_once_with(operations)
