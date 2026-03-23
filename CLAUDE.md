# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

TextFileLog は Windows 向けの tkinter GUI アプリケーションです。設定したテキストファイルを毎日アーカイブし、原本ファイルで上書きリセットします。Windows タスクスケジューラと連携してログオン時に自動実行できます。

## Commands

```bash
# アプリ起動（GUI）
python text_file_log.py

# 自動実行モード（GUI なし、タスクスケジューラ用）
python text_file_log.py --auto

# テスト実行
python -m pytest tests/ -v --tb=short

# 型チェック
pyright

# バージョン更新（patch）
python scripts/version_manager.py
```

## Architecture

### Core: `text_file_log.py`

すべてのコアロジックとUIを含むメインファイル。

- **`FileOperation`** (dataclass) — 1件の操作設定（名前、原本ファイル、指定ファイル、アーカイブ先）
- **`ConfigManager`** — `config.ini` の読み書き。`[operation_N]` セクション形式で操作を保存、`[general]` に `last_run` を記録
- **`FileProcessor`** — ファイル操作ロジック。指定ファイルの mtime が今日より古い場合のみアーカイブ（`{stem}{yymmdd}{suffix}` 形式）し原本で上書き
- **`TaskSchedulerManager`** — `schtasks` コマンドで Windows タスクスケジューラへの登録・削除
- **`MainApp`** (tk.Tk) — メインウィンドウ。起動時に `last_run` が今日でなければ自動実行
- **`SettingsDialog`** / **`OperationEditDialog`** — 操作設定の一覧・編集ダイアログ

### スキップ条件

`FileProcessor.process()` は以下の場合にスキップ（エラーなし）:
- 指定ファイルが存在しない
- 指定ファイルの mtime が今日以降（本日更新済み）

### その他のモジュール

- **`utils/config_manager.py`** — 汎用 config ユーティリティ（PyInstaller frozen 環境対応あり）
- **`scripts/version_manager.py`** — `app/__init__.py` と README.md のバージョン・日付を更新
- **`app/`**, **`service/`**, **`utils/`**, **`tests/`** — 将来の分割を想定したパッケージ構造（現在は stub）

### 設定ファイル

`config.ini` はスクリプトと同じディレクトリに生成される。バージョン情報は `app/__init__.py` の `__version__` と `__date__` で管理。

## Type Checking

`pyrightconfig.json` で `standard` モード、Python 3.13。チェック対象は `app`, `service`, `utils`, `tests`（`scripts/` は除外）。
