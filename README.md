# Kaggle Competition Watcher

Kaggle の Competitions を定期チェックし、指定キーワードに一致する新規コンペがあれば Slack に通知する Bot です。

## 概要

- Kaggle API でコンペ一覧を検索
- `KEYWORDS` と `CATEGORIES` に一致するコンペを抽出
- `kaggle_seen_competitions.json` で通知済みの `ref` を管理
- 新規コンペだけ Slack Incoming Webhook に通知
- GitHub Actions で毎日 JST 09:00 に実行

## 必要な Secrets

GitHub Actions では以下を設定します。

```text
KAGGLE_API_TOKEN
SLACK_WEBHOOK_URL
```

## ローカル実行

```bash
pip install -r requirements.txt
python watch_kaggle_competitions.py
```

ローカルでは `.env` に以下を設定できます。

```env
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
STATE_PATH="kaggle_seen_competitions.json"
NOTIFY_ON_FIRST_RUN=0
```

## ファイル

- `watch_kaggle_competitions.py`: 監視スクリプト
- `.github/workflows/watch.yml`: 定期実行 workflow
- `kaggle_seen_competitions.json`: 通知済みコンペの状態ファイル
