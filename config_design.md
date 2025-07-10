# Configuration Design

この文書では、Jun専用AIエージェントBotの設定ファイル構成と各項目についてまとめます。秘密情報は`.env`に、それ以外の動作設定は`config.yaml`に定義します。

## .env に入れる項目

- `DISCORD_TOKEN` ― Discord Botのトークン
- `OPENAI_API_KEY` ― OpenAI APIキー
- (必要に応じて) その他外部サービスの認証情報

例:
```env
DISCORD_TOKEN=xxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## config.yaml に入れる項目

- `openai.model` ― 使用するChatGPTモデル名
- `openai.temperature` ― 応答生成のtemperature値
- `discord.allowed_user_id` ― Botが反応を許可するDiscordユーザーID
- `discord.command_prefix` ―  (将来用) テキストコマンドのプレフィックス
- `reminder.check_interval` ― リマインダー確認間隔(秒)
- `database.path` ― SQLiteファイルのパス
- `timezone` ― デフォルトのタイムゾーン
- `logging.level` ― ログレベル (例: INFO)
- `logging.file` ― ログ出力先ファイル名

例:
```yaml
openai:
  model: gpt-4o-mini
  temperature: 0.7

discord:
  allowed_user_id: 123456789012345678
  command_prefix: "!"

reminder:
  check_interval: 60

database:
  path: "jun_assistant.db"

timezone: "Asia/Tokyo"

logging:
  level: INFO
  file: "junbot.log"
```

## 運用上のポイント

- `.env`はリポジトリに含めず、環境ごとに配置して`python-dotenv`で読み込みます。
- `config.yaml`はバージョン管理下に置き、必要に応じて値を変更することでBotの挙動を調整します。
- 起動時に`python-dotenv`と`PyYAML`でこれらを読み込み、`os.getenv()`や辞書から値を取得して各モジュールへ渡します。
