# Subscription Management App (Backend)

サブスクリプション・固定費を管理するアプリのバックエンドAPIです。

## 概要
このアプリは、毎月のサブスクや固定費を一覧で管理し、
「使っていないサービス」や「無駄な支出」を可視化することを目的としています。

## 主な機能（予定）
- サブスク・固定費の登録 / 編集 / 削除
- 月額・年額の合計金額の自動計算
- 解約候補の自動判定（将来対応）
- ダッシュボードでのグラフ表示

## 技術スタック
- Python: 3.11
- Framework: FastAPI
- ORM: SQLAlchemy 2.0
- Migration: Alembic
- Database: PostgreSQL
- Auth: Cognito JWT（想定）
- Infra (local): Docker / docker-compose
- Task Runner: Makefile

## ディレクトリ構成
```
subscription-app-backend/
├── app/
│   ├── api/            # APIルーティング
│   ├── core/           # 設定・DB接続
│   ├── models/         # SQLAlchemy モデル
│   ├── schemas/        # Pydantic スキーマ
│   └── main.py         # FastAPI エントリーポイント
├── alembic/            # マイグレーション
├── scripts/            # seed スクリプト
├── docker-compose.yml  # ローカルDB用
├── Makefile
├── alembic.ini
└── pyproject.toml
```

## 開発環境の起動
Backend の起動は以下のコマンドで行います。

```bash
make dev
```

このコマンドで以下を実行します。
- PostgreSQL の起動
- マイグレーションの適用
- 開発用データの seed 投入
- FastAPI の起動

### 起動後の URL
- Backend API:
http://127.0.0.1:8000

- OpenAPI (Swagger):
http://127.0.0.1:8000/docs

## 主な API
### カテゴリ
- カテゴリ一覧取得
- カテゴリ作成

### 支出
- 支出一覧取得
- 支出作成 / 更新 / 削除

### ダッシュボード
- 月額・年額合計の集計
- 月額・年額合計の集計
- 解約候補数の算出

## 環境変数
`.env` ファイルを作成してください。
※ .env.example を参考にしてください。

### フロントエンドについて
- フロントエンド（Next.js）は別リポジトリで管理しています
- フロントエンドは以下のリポジトリで起動してください

```bash
cd subscription-app-frontend
npm run dev
```

## 補足
- 本リポジトリは バックエンド API 専用です
- フロントエンドからの利用を前提に設計しています
- 将来的に以下を拡張予定です
  - 認証（Cognito）
  - 定期ジョブ（支払い履歴自動生成）
  - 解約候補判定ロジックの高度化