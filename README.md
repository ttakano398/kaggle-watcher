# Kaggle Competition Watcher

Kaggle Competitions から特定キーワードに一致する新規コンペを検知し、Slack Incoming Webhook に通知する Bot を段階的に実装するプロジェクトです。

このリポジトリでは、[docs/kaggle_watcher_codex_step0.md](docs/kaggle_watcher_codex_step0.md) の指示に従い、Step 1 以降を 1 ステップずつ進めます。

## Step 0

Step 0 は全体設計の確認です。まだ watcher 本体、Python 仮想環境、Slack Webhook、Kaggle API token、GitHub Actions workflow は作成しません。

次に進めるときは、以下のように依頼してください。

```text
Step 1 を進めて
```

## 重要な注意

- Slack Webhook URL はコードや README に直書きしない
- Kaggle API key はコードや README に直書きしない
- `.env` や `kaggle.json` は git 管理しない
- ユーザーが指定した Step だけを実装する

## 想定する最終構成

```text
kaggle-watcher/
├── .github/
│   └── workflows/
│       └── watch.yml
├── docs/
│   └── kaggle_watcher_codex_step0.md
├── watch_kaggle_competitions.py
├── requirements.txt
├── .gitignore
├── README.md
└── kaggle_seen_competitions.json
```
