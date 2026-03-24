import tkinter as tk
from pathlib import Path
from unittest.mock import patch

import pytest

from app.operation_edit_dialog import OperationEditDialog
from utils.models import FileOperation


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def _make_dialog(root: tk.Tk, op: FileOperation | None = None) -> OperationEditDialog:
    """grab_set をパッチしてモーダルロックを回避"""
    with patch.object(tk.Toplevel, "grab_set"):
        return OperationEditDialog(root, op)


def test_save_valid_inputs_sets_result(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("テスト操作")
    dlg._original.set("C:/original.txt")
    dlg._target.set("C:/target.txt")
    dlg._archive.set("C:/archive")

    dlg._save()

    assert dlg.result is not None
    assert dlg.result.name == "テスト操作"
    assert dlg.result.original_path == Path("C:/original.txt")
    assert dlg.result.target_path == Path("C:/target.txt")
    assert dlg.result.archive_dir == Path("C:/archive")


def test_save_valid_inputs_destroys_dialog(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("テスト操作")
    dlg._original.set("C:/original.txt")
    dlg._target.set("C:/target.txt")
    dlg._archive.set("C:/archive")

    with patch.object(dlg, "destroy") as mock_destroy:
        dlg._save()

    mock_destroy.assert_called_once()


def test_save_empty_name_shows_warning(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("")
    dlg._original.set("C:/original.txt")
    dlg._target.set("C:/target.txt")
    dlg._archive.set("C:/archive")

    with patch("app.operation_edit_dialog.messagebox.showwarning") as mock_warn, \
         patch.object(dlg, "destroy") as mock_destroy:
        dlg._save()

    mock_warn.assert_called_once()
    mock_destroy.assert_not_called()
    assert dlg.result is None
    dlg.destroy()


def test_save_empty_target_shows_warning(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("テスト操作")
    dlg._original.set("C:/original.txt")
    dlg._target.set("")
    dlg._archive.set("C:/archive")

    with patch("app.operation_edit_dialog.messagebox.showwarning") as mock_warn, \
         patch.object(dlg, "destroy") as mock_destroy:
        dlg._save()

    mock_warn.assert_called_once()
    mock_destroy.assert_not_called()
    assert dlg.result is None
    dlg.destroy()


def test_save_empty_archive_shows_warning(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("テスト操作")
    dlg._original.set("C:/original.txt")
    dlg._target.set("C:/target.txt")
    dlg._archive.set("")

    with patch("app.operation_edit_dialog.messagebox.showwarning") as mock_warn, \
         patch.object(dlg, "destroy") as mock_destroy:
        dlg._save()

    mock_warn.assert_called_once()
    mock_destroy.assert_not_called()
    assert dlg.result is None
    dlg.destroy()


def test_save_empty_original_shows_warning(tk_root):
    dlg = _make_dialog(tk_root)
    dlg._name_var.set("テスト操作")
    dlg._original.set("")
    dlg._target.set("C:/target.txt")
    dlg._archive.set("C:/archive")

    with patch("app.operation_edit_dialog.messagebox.showwarning") as mock_warn, \
         patch.object(dlg, "destroy") as mock_destroy:
        dlg._save()

    mock_warn.assert_called_once()
    mock_destroy.assert_not_called()
    assert dlg.result is None
    dlg.destroy()


def test_save_invalid_result_remains_none(tk_root):
    """バリデーション失敗時は result が None のまま"""
    dlg = _make_dialog(tk_root)
    # すべて空のまま

    with patch("app.operation_edit_dialog.messagebox.showwarning"):
        dlg._save()

    assert dlg.result is None
    dlg.destroy()


def test_edit_existing_operation_sets_initial_values(tk_root):
    """既存操作を渡すとフィールドに初期値が設定される"""
    op = FileOperation(
        name="既存操作",
        original_path=Path("C:/original.txt"),
        target_path=Path("C:/target.txt"),
        archive_dir=Path("C:/archive"),
    )
    dlg = _make_dialog(tk_root, op)

    assert dlg._name_var.get() == "既存操作"
    assert dlg._original.get() == "C:\\original.txt"
    assert dlg._target.get() == "C:\\target.txt"
    assert dlg._archive.get() == "C:\\archive"
    dlg.destroy()
