# DisCalendar Discord Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.4+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Discord用の予定管理Bot。[discalendar-next](https://github.com/Shirataki2/discalendar-next-v2) プロジェクトと連携して動作します。

## 📝 概要

DisCalendar Botは、Discordサーバー内で予定を管理するためのBotです。Supabaseをバックエンドとして使用し、Webアプリケーション（discalendar-next）と同じデータベースを共有します。これにより、DiscordとWebの両方から予定を管理できます。

## 機能

### Slashコマンド

| コマンド | 説明 | 権限 |
|----------|------|------|
| `/create` | 予定を新規作成 | 全員（制限モード時は管理者のみ） |
| `/list` | 予定一覧を表示（過去/未来/全て） | 全員 |
| `/init` | 通知先チャンネルを設定 | 管理者権限必須 |
| `/help` | ヘルプを表示 | 全員 |
| `/invite` | Bot招待URLを表示 | 全員 |

### バックグラウンドタスク

| タスク | 間隔 | 処理内容 |
|--------|------|----------|
| notify | 60秒 | 予定開始時刻に通知を送信 |
| presence | 10秒 | Botのステータス表示を更新 |

## 技術スタック

- **言語**: Python 3.12+
- **Discordフレームワーク**: discord.py 2.x
- **データベース**: Supabase (PostgreSQL)
- **DBクライアント**: supabase-py
- **パッケージ管理**: uv
- **ロギング**: structlog + AWS CloudWatch Logs

## セットアップ

### 1. 依存関係のインストール

```bash
# uvを使用
uv sync

# または pip
pip install -e .
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .env を編集して必要な値を設定
```

必要な環境変数:

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `BOT_TOKEN` | Discord Bot Token | ✅ |
| `APPLICATION_ID` | Discord Application ID | ✅ |
| `INVITATION_URL` | Bot招待URL | ✅ |
| `SUPABASE_URL` | SupabaseプロジェクトのURL | ✅ |
| `SUPABASE_SERVICE_KEY` | Supabaseのサービスロールキー | ✅ |
| `LOG_LEVEL` | ログレベル（デフォルト: INFO） | ❌ |
| `SENTRY_DSN` | Sentry DSN | ❌ |
| `AWS_REGION` | AWSリージョン（本番環境のみ） | ❌ |
| `AWS_CLOUDWATCH_LOG_GROUP` | CloudWatchロググループ名（本番環境のみ） | ❌ |

**注意**: AWS認証情報（`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`）は、本番環境では`~/.aws/credentials`ファイルに設定され、Docker awslogsドライバーがCloudWatch Logsにアクセスするために使用されます。コンテナの環境変数としては不要です。

### 3. Botの起動

```bash
# 開発環境
python -m src.main

# または
uv run python -m src.main
```

## Docker

### ビルドと起動

```bash
# ビルド
docker compose build

# 起動
docker compose up -d

# ログ確認
docker compose logs -f
```

> **注意**: 本番環境ではログはCloudWatch Logsに送信されます。ローカル開発環境では、CloudWatch設定がない場合は`json-file`ドライバーにフォールバックします。

## デプロイメント

本プロジェクトはTerraformとGitHub Actionsを使用してAWS Lightsailに自動デプロイされます。

詳細な手順は [デプロイメントガイド](docs/deployment.md) を参照してください。

### クイックスタート

1. **初回セットアップ**
   - S3バケットとDynamoDBテーブルを作成
   - GitHub OIDCプロバイダーを設定
   - `terraform/terraform.tfvars` を設定
   - 初回 `terraform apply` を実行

2. **GitHub Secretsの設定**
   - `AWS_ROLE_ARN`: Terraform出力から取得
   - `TF_STATE_BUCKET_NAME`: S3バケット名
   - `LIGHTSAIL_SSH_PRIVATE_KEY`: Lightsail SSH鍵
   - その他の環境変数（BOT_TOKEN等）

3. **自動デプロイ**
   - `main`ブランチにマージすると自動的にデプロイされます

詳細は [docs/deployment.md](docs/deployment.md) を参照してください。

## データベース

このBotは discalendar-next プロジェクトのSupabaseデータベースを共有します。

### 追加が必要なテーブル

以下のSQLをSupabase SQL Editorで実行してください:

```sql
-- event_settings（通知先チャンネル設定）
CREATE TABLE IF NOT EXISTS event_settings (
    id SERIAL PRIMARY KEY,
    guild_id VARCHAR(32) UNIQUE NOT NULL REFERENCES guilds(guild_id) ON DELETE CASCADE,
    channel_id VARCHAR(32) NOT NULL
);

-- guild_config（サーバー設定）
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id VARCHAR(32) PRIMARY KEY REFERENCES guilds(guild_id) ON DELETE CASCADE,
    restricted BOOLEAN NOT NULL DEFAULT false
);

-- 通知機能用カラム追加（既存のeventsテーブルに追加）
ALTER TABLE events ADD COLUMN IF NOT EXISTS notifications JSONB DEFAULT '[]'::jsonb;
```

## Bot権限

Bot招待時に必要な権限:
- `bot` scope
- `applications.commands` scope
- Permissions:
  - Send Messages
  - Embed Links
  - Use Slash Commands

## 開発

### コードフォーマット

```bash
# ruffでリント
uv run ruff check src/

# 自動修正
uv run ruff check --fix src/

# フォーマット
uv run ruff format src/
```

### テスト

```bash
# 全テスト実行
uv run pytest

# カバレッジ付き
uv run pytest --cov=src --cov-report=html

# 特定のテストのみ
uv run pytest tests/commands/test_create.py
```

### 型チェック

```bash
uv run mypy src/
```

## プロジェクト構成

```
src/
├── bot.py              # Botクラス定義
├── config.py           # 設定管理
├── main.py             # エントリーポイント
├── commands/           # Slashコマンド
│   ├── create.py       # 予定作成
│   ├── list_cmd.py     # 予定一覧
│   ├── init.py         # 初期設定
│   ├── help.py         # ヘルプ
│   └── invite.py       # 招待リンク
├── events/             # イベントハンドラ
│   └── guild.py        # サーバー参加/退出処理
├── tasks/              # バックグラウンドタスク
│   ├── notify.py       # 予定通知
│   └── presence.py     # ステータス更新
├── models/             # データモデル
│   ├── event.py        # イベントモデル
│   └── guild.py        # サーバーモデル
├── services/           # ビジネスロジック
│   ├── event_service.py
│   └── guild_service.py
└── utils/              # ユーティリティ
    ├── datetime.py     # 日時処理
    ├── embeds.py       # Embed生成
    └── permissions.py  # 権限チェック
```

## ロギング

### ローカル開発

ローカル開発環境では、ログはコンソールに出力されます。

```bash
python -m src.main
```

### 本番環境（CloudWatch Logs）

本番環境では、ログはAWS CloudWatch Logsに自動的に送信されます。

**AWSコンソールでの確認:**
1. CloudWatchサービスを開く
2. 「ログ」→「ロググループ」
3. `/aws/lightsail/discalendar-bot`を選択

**AWS CLIでの確認:**
```bash
# リアルタイムでログを表示
aws logs tail /aws/lightsail/discalendar-bot --follow

# エラーログのみフィルタ
aws logs filter-log-events \
  --log-group-name /aws/lightsail/discalendar-bot \
  --filter-pattern "ERROR"
```

## トラブルシューティング

### Botが起動しない

1. `.env` ファイルが正しく設定されているか確認
2. `BOT_TOKEN` が正しいか確認
3. Pythonバージョンが 3.12 以上か確認
4. 本番環境の場合、CloudWatch Logsでエラーログを確認

### Slashコマンドが表示されない

1. Botにアプリケーションコマンドの権限があるか確認
2. 起動ログで「Synced slash commands」が表示されているか確認
3. Discord上で少し時間を置いてから再度確認（最大1時間）

### 通知が送信されない

1. `/init` コマンドで通知先チャンネルを設定しているか確認
2. Botがそのチャンネルにメッセージを送信する権限があるか確認
3. 予定の開始時刻が正しく設定されているか確認

## 貢献

バグ報告や機能要望は、[Issues](https://github.com/yourusername/discalendar-next-bot/issues) からお願いします。

プルリクエストも歓迎します！以下の手順で開発に参加できます:

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 関連リンク

- [discalendar-next (Web App)](https://github.com/Shirataki2/discalendar-next-v2)
- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Supabase Documentation](https://supabase.com/docs)

## ライセンス

MIT License
