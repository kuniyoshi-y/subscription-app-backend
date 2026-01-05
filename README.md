# Subscription Management App (Backend)

サブスクリプション・固定費を管理するアプリのバックエンドAPIです。

---

## Overview
- 支出（expenses）
- カテゴリ（categories）
- ダッシュボード集計（dashboard/summary）

といったデータを提供する API を実装しています。

---

## API Endpoints
| Method | Path | Description |
|------|------|-------------|
| GET | /health | ヘルスチェック |
| GET | /expenses | 支出一覧 |
| POST | /expenses | 支出作成 |
| GET | /expenses/{id} | 支出詳細 |
| PATCH | /expenses/{id} | 支出更新 |
| DELETE | /expenses/{id} | 支出削除（論理削除） |
| GET | /categories | カテゴリ一覧 |
| POST | /categories | カテゴリ作成 |
| GET | /dashboard/summary | ダッシュボード集計 |

---

## Data Model Notes
- 主キーは UUID
- 論理削除：`deleted_at IS NULL`
- 開発・デモ用途として固定ユーザーIDを使用

---

## Architecture
```
Client
  ↓
API Gateway (HTTP API)
  ↓
AWS Lambda (Container Image / FastAPI)
  ↓
Neon PostgreSQL
```

---

## Tech Stack
- FastAPI
- SQLAlchemy 2.0
- Alembic（マイグレーション管理）
- PostgreSQL（Neon）

---

## Local Development
```bash
alembic upgrade head
uvicorn app.main:app --reload
```
- 環境変数：DATABASE_URL

---

## Deployment
Lambda + API Gateway + Neon：採用

結果として AWS 固定費ゼロ構成 を実現しています。

---

## CI/CD
- GitHub Actions
- OIDC による IAM Role Assume（アクセスキー未使用）
- main ブランチマージ時に：
  - Docker build
  - ECR push
  - Lambda update-function-code

---

## Directory Structure

```
subscription-app-backend/
├── app/
│   ├── api/            # APIルーティング（FastAPI router）
│   ├── core/           # 設定・DB接続・共通処理（環境変数など）
│   ├── models/         # SQLAlchemy モデル
│   ├── schemas/        # Pydantic スキーマ（Request/Response）
│   └── main.py         # FastAPI エントリーポイント
├── alembic/            # マイグレーション（revision / versions）
├── scripts/            # seed / 開発補助スクリプト
├── docker-compose.yml  # ローカルDB起動用（開発時のみ）
├── Makefile            # 開発用コマンド集（lint/test/migrate等）
├── alembic.ini         # Alembic 設定
└── pyproject.toml      # 依存管理（Poetry）

```

---

## Planned Features / TODO
今後、以下の機能拡張を予定しています。

- 認証・認可対応
  - JWT / Cognito 等によるユーザー認証
  - user_id をトークンベースで解決
- 権限制御
  - ユーザー単位でのデータアクセス制御
- バリデーション強化
  - リクエスト / レスポンススキーマの厳密化
- エラーハンドリング改善
  - FastAPI 標準の例外ハンドラ整理
- テスト追加
  - Unit Test
  - API テスト

---

## Related Repository
Frontend: https://github.com/kuniyoshi-y/subscription-app-frontend