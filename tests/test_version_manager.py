import re
from unittest.mock import mock_open, patch

from scripts.version_manager import (
    get_current_date,
    get_current_version,
    increment_version,
)


# --- increment_version ---

def test_increment_version_patch_normal():
    assert increment_version("1.2.3") == "1.2.4"


def test_increment_version_patch_carry():
    assert increment_version("1.2.9") == "1.2.10"


def test_increment_version_zero():
    assert increment_version("0.0.0") == "0.0.1"


def test_increment_version_large_numbers():
    assert increment_version("10.20.99") == "10.20.100"


def test_increment_version_invalid_returns_default():
    assert increment_version("invalid") == "0.0.0"


def test_increment_version_empty_string_returns_default():
    assert increment_version("") == "0.0.0"


# --- get_current_version ---

def test_get_current_version_returns_semver_format():
    version = get_current_version()
    assert re.match(r"^\d+\.\d+\.\d+$", version), f"SemVer 形式でない: {version}"


def test_get_current_version_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_current_version()
    assert result == "0.0.0"


def test_get_current_version_no_version_tag():
    """__version__ が含まれないファイルの場合は "0.0.0" を返す"""
    with patch("builtins.open", mock_open(read_data="# no version here\n")):
        result = get_current_version()
    assert result == "0.0.0"


# --- get_current_date ---

def test_get_current_date_returns_date_format():
    date = get_current_date()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", date), f"YYYY-MM-DD 形式でない: {date}"


def test_get_current_date_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_current_date()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result)


def test_get_current_date_no_date_tag():
    """__date__ が含まれないファイルの場合は現在日付を返す"""
    with patch("builtins.open", mock_open(read_data="# no date here\n")):
        result = get_current_date()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result)
