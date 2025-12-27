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
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy / Alembic

## 開発状況
現在はバックエンドの基盤構築中です。

## 開発環境の起動
開発用のセットアップ・起動は Makefile にまとめています。
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
- Backend API: http://127.0.0.1:8000

### 補足
- フロントエンド（Next.js）は別リポジトリで管理しています
- フロントエンドは以下のリポジトリで起動してください

```bash
cd subscription-app-frontend
npm run dev
```