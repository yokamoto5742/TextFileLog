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
