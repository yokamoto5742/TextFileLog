# TextFileLog

原本ファイルを管理し、作業用コピーに同期させるための Windows ユーティリティです。変更されたファイルはタイムスタンプ付きでアーカイブされます。

## 機能

- オリジナルファイルと作業コピーの同期管理
- 変更前の作業ファイルを自動アーカイブ（`filename_YYMMDD_HHMMSS.txt` 形式）
- GUI と自動実行モードの両方をサポート
- Windowsスタートアップへの自動登録機能

## 動作環境

- Windows 11
- Python 3.13 以上

## インストール

1. リポジトリをクローン

```bash
git clone <repository-url>
cd TextFileLog
```

2. 仮想環境を作成

```bash
python -m venv .venv
```

3. 仮想環境を有効化

```bash
# Windows の場合
.venv\Scripts\activate
```

4. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### GUI モード

```bash
python main.py
```

- ファイル操作一覧を表示
- 「実行」ボタンで各操作を実行
- 「設定」ボタンで操作の追加・編集・削除
- 「自動実行登録」でシステム起動時の自動実行を登録

### 自動実行モード（GUI なし）

```bash
python main.py --auto
```

設定されたすべての操作を実行して終了します。

### 操作の設定

`utils/config.ini` でファイル操作を定義します。

```ini
[operation_1]
name = 操作の表示名
target_path = C:\path\to\working.txt
archive_dir = C:\path\to\archive
original_path = C:\path\to\original.txt
```

各セクションの説明：
- `name` ：操作の表示名
- `target_path` ：指定ファイル（オーバーライトされる対象）
- `archive_dir` ：変更されたファイルのアーカイブ先
- `original_path` ：原本ファイル（読み取り専用）

## プロジェクト構造

```
TextFileLog/
├── main.py                      # エントリポイント
├── app/                         # GUI層
│   ├── main_window.py          # メインウィンドウ
│   ├── settings_dialog.py       # 設定ダイアログ
│   └── operation_edit_dialog.py # 操作編集ダイアログ
├── service/                     # ビジネスロジック層
│   ├── file_processor.py        # ファイル同期処理
│   └── startup_manager.py       # Windows スタートアップ管理
├── utils/                       # ユーティリティ層
│   ├── config_manager.py        # 設定管理
│   ├── models.py                # データモデル
│   └── config.ini               # 設定ファイル
├── scripts/                     # ビルド・管理スクリプト
│   └── version_manager.py       # バージョン管理
└── tests/                       # テストファイル
```

## 主要な機能

### FileOperation

ファイル操作の基本単位を表すデータモデル。

```python
@dataclass
class FileOperation:
    name: str           # 操作の表示名
    target_path: Path   # 作業コピーのパス
    archive_dir: Path   # アーカイブディレクトリ
    original_path: Path # オリジナルファイルのパス
```

### FileProcessor

ファイルの同期処理を実行します。

```python
processor = FileProcessor()
results = processor.process_all(operations)
```

処理フロー：
1. ターゲットファイルが存在するか確認
2. 原本ファイルが存在するか確認
3. ターゲットファイルが原本ファイルより新しいか確認
4. 新しい場合：ターゲットファイルを archive_dir にアーカイブしてから原本ファイルで上書き

### ConfigManager

`config.ini` から操作を読み込み・保存します。

```python
config = ConfigManager()
operations = config.load()      # 設定を読み込む
config.save(operations)          # 設定を保存
task_name, run_key = config.load_startup()  # スタートアップ設定を読み込む
```

## 開発

### テスト実行

```bash
# すべてのテストを実行
python -m pytest tests/ -v --tb=short

# 特定のテストファイルを実行
python -m pytest tests/test_models.py -v
```

### 型チェック

```bash
pyright
```

### Windows 実行ファイルのビルド

```bash
python build.py
```

バージョンが自動でインクリメントされ、PyInstaller で `.exe` をビルドします。生成物には `config.ini` が含まれます。

## トラブルシューティング

**「ファイルが見つかりません」エラーが出る**
- `original_path` と `target_path` が正しいか確認してください
- パスが存在することを確認してください

**自動実行に登録されない**
- Windows レジストリの書き込み権限があるか確認してください
- `config.ini` の `[startup]` セクション設定を確認してください

**アーカイブが作成されない**
- `archive_dir` が有効なパスか確認してください
- ファイルシステムの書き込み権限があるか確認してください

**ターゲットファイルが更新されない**
- ターゲットがオリジナルより新しい場合のみ処理されます
- ファイルの更新日時を確認してください

## バージョン情報

- **現在のバージョン**: 1.0.2
- **最終更新日**: 2026年03月25日

## ライセンス

このプロジェクトのライセンス情報については、 [LICENSE](./LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](./CHANGELOG.md) を参照してください。
