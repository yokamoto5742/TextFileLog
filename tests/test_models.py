from pathlib import Path

import pytest

from utils.models import FileOperation


@pytest.fixture
def sample_op(tmp_path) -> FileOperation:
    return FileOperation(
        name="テスト操作",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )


def test_fields_are_stored_correctly(tmp_path):
    op = FileOperation(
        name="テスト",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )
    assert op.name == "テスト"
    assert op.original_path == tmp_path / "original.txt"
    assert op.target_path == tmp_path / "target.txt"
    assert op.archive_dir == tmp_path / "archive"


def test_path_fields_are_path_instances(sample_op):
    assert isinstance(sample_op.original_path, Path)
    assert isinstance(sample_op.target_path, Path)
    assert isinstance(sample_op.archive_dir, Path)


def test_equality_same_values(tmp_path):
    op1 = FileOperation(
        name="テスト",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )
    op2 = FileOperation(
        name="テスト",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )
    assert op1 == op2


def test_inequality_different_name(tmp_path):
    op1 = FileOperation(
        name="テスト1",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )
    op2 = FileOperation(
        name="テスト2",
        original_path=tmp_path / "original.txt",
        target_path=tmp_path / "target.txt",
        archive_dir=tmp_path / "archive",
    )
    assert op1 != op2


def test_str_path_is_not_auto_converted():
    """dataclass は型変換しないため str を渡すと str のまま保持される"""
    op = FileOperation(
        name="テスト",
        original_path="/some/path/original.txt",  # type: ignore[arg-type]
        target_path="/some/path/target.txt",       # type: ignore[arg-type]
        archive_dir="/some/archive",               # type: ignore[arg-type]
    )
    assert isinstance(op.original_path, str)
    assert not isinstance(op.original_path, Path)
