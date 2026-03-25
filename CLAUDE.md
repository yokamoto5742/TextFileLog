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

## Project Overview

TextFileLog is a Windows utility (Windows 11 only) that manages original/template files and synchronizes them with working copies. When a working copy is newer than the original, it archives the working copy with a timestamp and overwrites it with the original.

## Commands

```bash
# Run (GUI mode)
python main.py

# Run (headless/auto mode)
python main.py --auto

# Tests
python -m pytest tests/ -v --tb=short

# Run a single test file
python -m pytest tests/test_models.py -v

# Type checking
pyright

# Build executable (increments patch version, creates dist/TextFileLog.exe)
python build.py
```

## Architecture

Three-layer clean architecture:

```
app/        ← GUI (Tkinter): main_window, settings_dialog, operation_edit_dialog
service/    ← Business logic: file_processor (sync/archive), startup_manager (Windows registry)
utils/      ← Data: models (FileOperation dataclass), config_manager (INI read/write)
```

**Data flow:** `ConfigManager` loads `FileOperation` list from `utils/config.ini` → `FileProcessor` processes each operation → results logged to GUI or stdout.

### FileProcessor logic (core)

For each `FileOperation`:
1. If target doesn't exist → skip
2. If original doesn't exist → error
3. If target is **newer** than original → archive target as `filename_YYMMDD_HHMMSS.ext`, then overwrite target with original
4. If target is older → skip

### Startup integration

`StartupManager` writes/removes a registry entry at `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` pointing to `pythonw.exe main.py --auto`.

### Config file format (`utils/config.ini`)

```ini
[startup]
task_name = TextFileLog
run_key = Software\Microsoft\Windows\CurrentVersion\Run

[operation_1]
name = Display Name
original_path = C:\path\to\original.txt
target_path = C:\path\to\working.txt
archive_dir = C:\path\to\archive
```

`ConfigManager` detects PyInstaller frozen mode (`sys.frozen`) and adjusts paths accordingly — config.ini is bundled into the exe.

## Key Details

- All UI text and log messages are in Japanese
- Version is tracked in `app/__init__.py` (`__version__`, `__date__`) and updated by `scripts/version_manager.py` (called automatically by `build.py`)
- `MainApp` does NOT auto-run on startup in GUI mode; auto-run only happens in `--auto` (headless) mode
- Log message prefixes: `[処理済]` (processed), `[スキップ]` (skipped), `[エラー]` (error)
