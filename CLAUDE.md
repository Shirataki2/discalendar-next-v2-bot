# DisCalendar Bot - AI Development Guide

このドキュメントは、AI（特に Claude）がこのプロジェクトを理解し、効率的に開発支援を行うためのガイドです。

## プロジェクト概要

### 目的
Discord上で予定を管理するためのBot。Webアプリケーション（discalendar-next）と同じSupabaseデータベースを共有し、Discord/Web両方から予定を管理できる。

### 技術スタック
- **言語**: Python 3.12+
- **Discord**: discord.py 2.4+ (Slash Commands)
- **DB**: Supabase (PostgreSQL)
- **パッケージ管理**: uv
- **ロギング**: structlog + AWS CloudWatch Logs
- **テスト**: pytest, pytest-asyncio, pytest-mock
- **インフラ**: AWS Lightsail + Terraform + GitHub Actions

## アーキテクチャ

### レイヤー構造

```
┌─────────────────────────────────┐
│  Discord Interface Layer        │
│  (commands/, events/, tasks/)   │
├─────────────────────────────────┤
│  Business Logic Layer           │
│  (services/)                    │
├─────────────────────────────────┤
│  Data Access Layer              │
│  (models/)                      │
├─────────────────────────────────┤
│  Infrastructure Layer           │
│  (Supabase Client)              │
└─────────────────────────────────┘
```

### 主要コンポーネント

#### 1. Bot Core (`src/bot.py`)
- `DisCalendarBot`: メインのBotクラス
- Supabaseクライアントの初期化
- サービスインスタンスの管理
- Cog（拡張機能）のロード

#### 2. Commands (`src/commands/`)
Slash Command の実装。すべて `discord.ext.commands.Cog` を継承。

- `create.py`: `/create` - 予定作成（モーダルフォーム使用）
- `list_cmd.py`: `/list` - 予定一覧表示（選択肢: past/future/all）
- `init.py`: `/init` - 通知チャンネル設定（管理者権限必須）
- `help.py`: `/help` - ヘルプ表示
- `invite.py`: `/invite` - 招待リンク表示

#### 3. Events (`src/events/`)
Discordイベントハンドラ。

- `guild.py`: 
  - `on_guild_join`: サーバー参加時にDB登録
  - `on_guild_remove`: サーバー退出時にDB削除
  - `on_guild_update`: サーバー情報更新時にDB更新

#### 4. Tasks (`src/tasks/`)
バックグラウンドタスク（`discord.ext.tasks` 使用）。

- `notify.py`: 60秒ごとに実行、予定開始時刻に通知送信
- `presence.py`: 10秒ごとに実行、Botのステータス更新

#### 5. Services (`src/services/`)
ビジネスロジックとデータベースアクセスを抽象化。

- `guild_service.py`: サーバー情報のCRUD、設定管理
- `event_service.py`: 予定のCRUD、通知管理

#### 6. Models (`src/models/`)
データモデル（Pydanticではなく、シンプルなdataclass使用）。

- `guild.py`: Guild, GuildConfig, EventSettings
- `event.py`: Event

#### 7. Utils (`src/utils/`)
共通ユーティリティ関数。

- `embeds.py`: Discord Embed生成ヘルパー
- `permissions.py`: 権限チェックヘルパー
- `datetime.py`: 日時処理ヘルパー（JST変換など）

## データベーススキーマ

### 既存テーブル（discalendar-nextで管理）

#### `guilds`
```sql
guild_id VARCHAR(32) PRIMARY KEY  -- Discord Server ID
name VARCHAR(100)                 -- サーバー名
avatar_url VARCHAR(512)           -- アイコンURL
locale VARCHAR(10) DEFAULT 'ja'   -- 言語設定
```

#### `events`
```sql
id UUID PRIMARY KEY
guild_id VARCHAR(32) FK → guilds
name VARCHAR(255)                 -- 予定名
description TEXT                  -- 説明
color VARCHAR(7)                  -- カラーコード (#RRGGBB)
is_all_day BOOLEAN                -- 終日フラグ
start_at TIMESTAMPTZ             -- 開始日時
end_at TIMESTAMPTZ               -- 終了日時
location VARCHAR(255)             -- 場所
channel_id VARCHAR(32)            -- 関連チャンネルID
channel_name VARCHAR(100)         -- チャンネル名
notifications JSONB DEFAULT '[]'  -- 通知済みユーザーリスト
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

### Bot専用テーブル

#### `event_settings`
```sql
id SERIAL PRIMARY KEY
guild_id VARCHAR(32) UNIQUE FK → guilds
channel_id VARCHAR(32)            -- 通知先チャンネルID
```

#### `guild_config`
```sql
guild_id VARCHAR(32) PRIMARY KEY FK → guilds
restricted BOOLEAN DEFAULT false  -- 制限モード（管理者のみ作成可）
```

## コーディング規約

### 一般原則
1. **型アノテーション**: すべての関数・メソッドに型アノテーションを付ける
2. **Docstring**: すべての関数・クラスに詳細なdocstringを記述（Google Style）
3. **エラーハンドリング**: 適切な例外処理とログ記録
4. **非同期処理**: discord.pyは非同期なので、I/O処理は必ず `async`/`await`

### スタイルガイド
- **リンター**: Ruff（`ruff check`, `ruff format`）
- **行長**: 100文字以内
- **インポート**: 標準ライブラリ → サードパーティ → ローカル
- **命名**: 
  - 関数・変数: `snake_case`
  - クラス: `PascalCase`
  - 定数: `UPPER_SNAKE_CASE`

### discord.py パターン

#### Cogの基本構造
```python
from discord import app_commands
from discord.ext import commands
import structlog

logger = structlog.get_logger()

class MyCog(commands.Cog):
    """Cog description."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="mycommand", description="...")
    async def my_command(
        self, 
        interaction: discord.Interaction,
        # パラメータ
    ) -> None:
        """Command implementation."""
        try:
            # 処理前応答（3秒以内に必須）
            await interaction.response.defer(ephemeral=True)
            
            # 実際の処理
            result = await some_async_operation()
            
            # フォローアップ応答
            await interaction.followup.send(result)
            
        except Exception as e:
            logger.exception("Error in mycommand", error=str(e))
            await interaction.followup.send(
                "エラーが発生しました",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    """Required setup function for Cog loading."""
    await bot.add_cog(MyCog(bot))
```

#### タスクの基本構造
```python
from discord.ext import tasks, commands
import structlog

logger = structlog.get_logger()

class MyTask(commands.Cog):
    """Task description."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.my_loop.start()
    
    def cog_unload(self) -> None:
        """Stop task when cog is unloaded."""
        self.my_loop.cancel()
    
    @tasks.loop(seconds=60)
    async def my_loop(self) -> None:
        """Task implementation."""
        try:
            # 処理
            pass
        except Exception as e:
            logger.exception("Error in my_loop", error=str(e))
    
    @my_loop.before_loop
    async def before_my_loop(self) -> None:
        """Wait until bot is ready."""
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyTask(bot))
```

### Supabase パターン

#### データ取得
```python
# 単一レコード
response = supabase.table("events")\
    .select("*")\
    .eq("id", event_id)\
    .single()\
    .execute()
event = response.data

# 複数レコード
response = supabase.table("events")\
    .select("*")\
    .eq("guild_id", guild_id)\
    .order("start_at")\
    .execute()
events = response.data
```

#### データ挿入
```python
response = supabase.table("events")\
    .insert({
        "guild_id": guild_id,
        "name": name,
        "start_at": start_at.isoformat(),
        # ...
    })\
    .execute()
```

#### データ更新
```python
response = supabase.table("events")\
    .update({"name": new_name})\
    .eq("id", event_id)\
    .execute()
```

#### データ削除
```python
response = supabase.table("events")\
    .delete()\
    .eq("id", event_id)\
    .execute()
```

#### JOIN（関連データ取得）
```python
# event_settings と JOIN
response = supabase.table("events")\
    .select("*, event_settings!inner(channel_id)")\
    .eq("guild_id", guild_id)\
    .execute()
```

## テスト戦略

### テストの種類
1. **Unit Tests**: Services, Utils の単体テスト
2. **Integration Tests**: Supabase との連携テスト（モック使用）
3. **Command Tests**: Slash Command の動作テスト（モック使用）

### テスト構造
```python
import pytest
from pytest_mock import MockerFixture
from discord.ext import commands

@pytest.mark.asyncio
async def test_something(mocker: MockerFixture) -> None:
    """Test description."""
    # モック作成
    mock_interaction = mocker.AsyncMock()
    
    # テスト実行
    result = await some_function(mock_interaction)
    
    # アサーション
    assert result == expected_value
    mock_interaction.response.send_message.assert_called_once()
```

### モックの使い方
- `pytest-mock` の `mocker` フィクスチャを使用
- Supabase レスポンスは `MockResponse` クラスでモック
- Discord オブジェクトは `mocker.AsyncMock()` でモック

## よくある変更パターン

### 新しいSlashコマンドを追加
1. `src/commands/` に新ファイル作成
2. `Cog` クラスを定義し、`@app_commands.command` でコマンド実装
3. `async def setup(bot)` を定義
4. `src/bot.py` の `setup_hook` に `await self.load_extension("src.commands.new_cmd")` を追加
5. `tests/commands/` にテストファイル作成

### 新しいバックグラウンドタスクを追加
1. `src/tasks/` に新ファイル作成
2. `Cog` クラスを定義し、`@tasks.loop` でタスク実装
3. `before_loop` で `await self.bot.wait_until_ready()` を実装
4. `src/bot.py` の `setup_hook` に `await self.load_extension("src.tasks.new_task")` を追加

### データベーステーブルを追加
1. README.md のデータベーススキーマセクションに SQL を追加
2. `src/models/` に対応するモデルクラスを追加
3. `src/services/` に対応するサービスクラスを追加

### 新しいEmbed形式を追加
1. `src/utils/embeds.py` に関数を追加
2. 適切なカラー、フィールド、フッターを設定
3. テストを `tests/utils/test_embeds.py` に追加

## デバッグのヒント

### ログの確認
- `structlog` を使用し、構造化ログで出力
- ログレベルは環境変数 `LOG_LEVEL` で制御
- 重要なイベント（コマンド実行、DB操作、エラー）は必ずログ記録
- **本番環境**: AWS CloudWatch Logsに自動送信（Docker awslogsドライバー使用）
  - ロググループ: `/aws/lightsail/discalendar-bot`
  - ログストリーム: `discalendar-bot`
  - AWSコンソールまたはCLI (`aws logs tail`) で確認可能
- **ローカル開発**: コンソールまたはDockerログ (`docker compose logs`) で確認

### よくあるエラー

#### `Interaction did not respond in time`
- 原因: Interactionに3秒以内に応答していない
- 解決: `await interaction.response.defer()` を最初に呼ぶ

#### `Missing Access`
- 原因: Botが必要な権限を持っていない
- 解決: Bot招待時の権限設定を確認

#### `Unknown Channel`
- 原因: チャンネルIDが無効、またはBotがアクセスできない
- 解決: チャンネルの存在確認と権限確認

### Discord Developer Portal
- Bot Token: Bot セクション
- Application ID: General Information
- OAuth2 URL Generator: OAuth2 セクション
- 必要な Scopes: `bot`, `applications.commands`
- 必要な Permissions: Send Messages, Embed Links

## 環境変数

```env
# 必須
BOT_TOKEN=               # Discord Bot Token
APPLICATION_ID=          # Discord Application ID
SUPABASE_URL=           # Supabase Project URL
SUPABASE_SERVICE_KEY=   # Supabase Service Role Key

# オプション
INVITATION_URL=         # Bot招待URL
LOG_LEVEL=INFO          # ログレベル (DEBUG/INFO/WARNING/ERROR)
SENTRY_DSN=            # Sentryエラー追跡

# AWS CloudWatch Logs（本番環境のみ）
AWS_ACCESS_KEY_ID=           # CloudWatch用アクセスキーID
AWS_SECRET_ACCESS_KEY=       # CloudWatch用シークレットアクセスキー
AWS_REGION=ap-northeast-1    # AWSリージョン
AWS_CLOUDWATCH_LOG_GROUP=    # CloudWatchロググループ名（例: /aws/lightsail/discalendar-bot）
```

## 開発フロー

### ローカル開発
1. `uv sync` で依存関係インストール
2. `.env` ファイル作成・設定
3. `python -m src.main` で起動
4. Discord Developer Portalでテストサーバーに招待

### テスト
1. 単体テスト: `uv run pytest tests/`
2. カバレッジ確認: `uv run pytest --cov=src`
3. リント: `uv run ruff check src/`
4. フォーマット: `uv run ruff format src/`
5. 型チェック: `uv run mypy src/`

### デプロイ
1. Docker: `docker compose build && docker compose up -d`
2. ログ確認: `docker compose logs -f`

## 参考リンク

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## 注意事項

### セキュリティ
- `BOT_TOKEN` は絶対にコミットしない
- Supabase の `service_role` キーは強力な権限を持つため、Bot専用環境でのみ使用
- 環境変数は `.env` ファイルまたは Docker Secrets で管理

### パフォーマンス
- 大量のイベントを扱う場合は、ページネーション実装を検討
- 通知タスクは現在60秒間隔だが、負荷に応じて調整可能
- Supabase のクエリは適切にインデックスを活用

### タイムゾーン
- データベースは UTC で保存（`TIMESTAMPTZ`）
- 表示時は JST（UTC+9）に変換
- `src/utils/datetime.py` の関数を使用
