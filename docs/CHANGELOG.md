# Changelog

このプロジェクトのすべての主な変更は、このファイルに記録されます。

このファイルのフォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

## [1.0.1] - 2026-03-24
安定版初回リリース

### 追加

- ConfigManager に startup 設定の読み込み機能を追加
- 設定ダイアログを新規作成し、ファイル操作の追加・編集・削除機能を提供
- OperationEditDialog のファイル選択ダイアログを整理

### 変更

- スタートアップ設定を config.ini に移動
- スタートアップ登録・解除処理を config.ini から読み込むように変更
- スタートアップ登録ボタンの文言を「自動実行登録」に変更
- OperationEditDialog のUI を改善
- ボタン配置を調整し、左寄せを追加

### 修正

- ファイルアーカイブ時のログメッセージを修正
- ファイル操作がない場合のメッセージを修正

[1.0.1]: https://github.com/yourusername/TextFileLog/releases/tag/1.0.1
