# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返す。
- コードの変更範囲は最小限に抑える。
- コードの修正は直接適用する。
- Pythonのコーディング規約はPEP8に従います。
- KISSの原則に従い、できるだけシンプルなコードにします。
- 可読性を優先します。一度読んだだけで理解できるコードが最高のコードです。
- Pythonのコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

## クリーンコードガイドライン
- 関数のサイズ：関数は50行以下に抑えることを目標にしてください。関数の処理が多すぎる場合は、より小さな関数に分割してください。
- 単一責任：各関数とモジュールには明確な目的が1つあるようにします。無関係なロジックをまとめないでください。
- 命名：説明的な名前を使用してください。`tmp` 、`data`、`handleStuff`のような一般的な名前は避けてください。例えば、`doCalc`よりも`calculateInvoiceTotal` の方が適しています。
- DRY原則：コードを重複させないでください。類似のロジックが2箇所に存在する場合は、共有関数にリファクタリングしてください。それぞれに独自の実装が必要な場合はその理由を明確にしてください。
- コメント:分かりにくいロジックについては説明を加えます。説明不要のコードには過剰なコメントはつけないでください。
- コメントとdocstringは必要最小限に日本語で記述します。
- このアプリのUI画面で表示するメッセージはすべて日本語にします。

## Commands

```bash
# Run GUI mode
python main.py

# Run headless auto mode (no GUI, processes all operations and exits)
python main.py --auto

# Run tests
python -m pytest tests/ -v --tb=short

# Run a single test file
python -m pytest tests/test_models.py -v

# Type check
pyright

# Build Windows executable
python build.py
```

## Architecture

**TextFileLog** is a Windows utility that maintains template/original files and syncs them to working copies, creating timestamped archives of changes.

### Layer Structure

- `main.py` — Entry point. Routes to GUI (`MainApp`) or headless (`run_auto()`) based on `--auto` flag.
- `app/` — Tkinter GUI layer (main window, settings dialog, operation edit dialog)
- `service/` — Business logic (file processing, Windows startup/registry management)
- `utils/` — Data models, config management, and `config.ini` storage

### Core Data Flow

1. `ConfigManager` loads `FileOperation` objects from `config.ini` (one INI section per operation)
2. `FileProcessor.process_all()` executes each operation:
   - If target is newer than original → archive target as `filename_YYMMDD_HHMMSS.ext`, then overwrite target with original
3. Results are displayed in the GUI log panel or stdout (auto mode)

### Key Model

```python
@dataclass
class FileOperation:
    name: str           # Display name
    original_path: Path # Source/template (read-only reference)
    target_path: Path   # Working file (gets overwritten)
    archive_dir: Path   # Where modified targets are archived
```

### Windows Startup Integration

`service/startup_manager.py` writes to the Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`) to run `main.py --auto` on system startup.

### Configuration

`utils/config.ini` is the single source of truth for all operations and startup settings. `ConfigManager` handles path resolution for both dev (Python) and production (PyInstaller frozen) environments.

## Testing

Tests use `pytest` with `unittest.mock`. Test files follow the pattern `tests/test_<module>.py`. Mocking strategy: patch at the call site (e.g., `patch("app.main_window.ConfigManager")`), not at the definition.

## Build

`build.py` auto-increments the version (via `scripts/version_manager.py`), then runs PyInstaller to produce a single `.exe` bundled with `config.ini`.

## Notes

- All UI strings are in Japanese.
- `pyrightconfig.json` targets Python 3.13; `scripts/` is excluded from type checking.
- PyInstaller frozen detection: `sys.frozen` attribute is checked in `ConfigManager` to resolve paths correctly when running as `.exe`.
