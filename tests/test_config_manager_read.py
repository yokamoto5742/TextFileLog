import configparser

from utils.config_manager import ConfigManager


def test_read_returns_empty_parser_when_file_not_found(tmp_path):
    """config.ini が存在しない場合、空の ConfigParser を返す"""
    cm = ConfigManager(tmp_path / "nonexistent.ini")
    cp = cm._read()
    assert cp.sections() == []


def test_read_returns_empty_parser_for_empty_file(tmp_path):
    """空の config.ini の場合、空の ConfigParser を返す"""
    config_file = tmp_path / "config.ini"
    config_file.write_text("", encoding="utf-8")
    cm = ConfigManager(config_file)
    cp = cm._read()
    assert cp.sections() == []


def test_read_returns_sections_from_valid_file(tmp_path):
    """正常な config.ini からセクションを読み込む"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[operation_1]\nname = テスト\n[startup]\ntask_name = App\n",
        encoding="utf-8",
    )
    cm = ConfigManager(config_file)
    cp = cm._read()
    assert "operation_1" in cp.sections()
    assert "startup" in cp.sections()


def test_read_returns_configparser_instance(tmp_path):
    """戻り値が ConfigParser インスタンスである"""
    cm = ConfigManager(tmp_path / "nonexistent.ini")
    cp = cm._read()
    assert isinstance(cp, configparser.ConfigParser)


def test_read_utf8_encoding(tmp_path):
    """UTF-8 の日本語を含むファイルを正しく読む"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[operation_1]\nname = 日本語テスト\n",
        encoding="utf-8",
    )
    cm = ConfigManager(config_file)
    cp = cm._read()
    assert cp.get("operation_1", "name") == "日本語テスト"


def test_read_is_idempotent(tmp_path):
    """同じファイルを 2 回読んでも同じ結果を返す"""
    config_file = tmp_path / "config.ini"
    config_file.write_text("[operation_1]\nname = テスト\n", encoding="utf-8")
    cm = ConfigManager(config_file)
    cp1 = cm._read()
    cp2 = cm._read()
    assert cp1.sections() == cp2.sections()
