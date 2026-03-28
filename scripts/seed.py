from __future__ import annotations

import uuid
from datetime import date
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.user import User
from app.models.usage_status import UsageStatus
from app.models.category import Category, CategoryType
from app.models.expense import Expense, BillingCycle


DEV_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def upsert_dev_user(db: Session) -> User:
    """開発用固定ユーザーを投入（存在すれば再利用）"""
    existing = db.get(User, DEV_USER_ID)
    if existing:
        return existing

    user = User(
        id=DEV_USER_ID,
        email="dev@example.com",
        name="Dev User",
    )
    db.add(user)
    db.flush()
    return user


def upsert_usage_statuses(db: Session) -> None:
    """UsageStatusマスタを投入（idが存在すれば再利用）"""
    masters = [
        {'id': 1, 'label': 'よく使う',   'score': 3},
        {'id': 2, 'label': 'たまに',     'score': 2},
        {'id': 3, 'label': '使ってない', 'score': 1},
    ]
    for m in masters:
        existing = db.get(UsageStatus, m['id'])
        if existing:
            existing.label = m['label']
            existing.score = m['score']
        else:
            db.add(UsageStatus(**m))
    db.flush()


def upsert_categories(db: Session) -> list[Category]:
    """
    システム標準カテゴリを投入（同名があれば再利用）
    ※ is_system_default=True, user_id=None を前提
    """
    seeds = [
        dict(name="動画配信", type=CategoryType.subscription, sort_order=10),
        dict(name="家賃", type=CategoryType.fixed, sort_order=1),
        dict(name="保険", type=CategoryType.fixed, sort_order=2),
        dict(name="携帯", type=CategoryType.semi_fixed, sort_order=20),
        dict(name="その他", type=CategoryType.semi_fixed, sort_order=99),
    ]

    result: list[Category] = []

    for s in seeds:
        existing = db.execute(
            select(Category).where(
                Category.name == s["name"],
                Category.is_system_default.is_(True),
                Category.user_id.is_(None),
                Category.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if existing:
            # 必要なら最新化（type/sort_orderが変わった時にも追従）
            existing.type = s["type"]
            existing.sort_order = s["sort_order"]
            result.append(existing)
            continue

        c = Category(
            user_id=None,
            name=s["name"],
            type=s["type"],
            is_system_default=True,
            sort_order=s["sort_order"],
        )
        db.add(c)
        result.append(c)

    db.flush()  # id採番
    return result


def upsert_expenses(db: Session, categories: Iterable[Category]) -> None:
    """
    デモ用支出を投入（同名 + user_id + deleted_at is null をキーに再利用）
    """
    cat_by_name = {c.name: c for c in categories}

    seeds = [
        dict(
            name="Netflix",
            category_name="動画配信",
            amount=990,
            billing_cycle=BillingCycle.monthly,
            next_billing_date=date.today(),
            auto_renewal=True,
            is_fixed=False,
            is_subscription=True,
            is_review_target=True,
            manual_cancel_suggestion=None,
            auto_cancel_suggestion=False,
            cancel_suggestion=False,
            memo="デモデータ",
        ),
        dict(
            name="家賃",
            category_name="家賃",
            amount=70000,
            billing_cycle=BillingCycle.monthly,
            next_billing_date=date.today(),
            auto_renewal=True,
            is_fixed=True,
            is_subscription=False,
            is_review_target=False,
            manual_cancel_suggestion=None,
            auto_cancel_suggestion=False,
            cancel_suggestion=False,
            memo="デモデータ",
        ),
    ]

    for s in seeds:
        category = cat_by_name[s["category_name"]]

        existing = db.execute(
            select(Expense).where(
                Expense.user_id == DEV_USER_ID,
                Expense.name == s["name"],
                Expense.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        if existing:
            # 必要なら最新化
            existing.category_id = category.id
            existing.amount = s["amount"]
            existing.billing_cycle = s["billing_cycle"]
            existing.next_billing_date = s["next_billing_date"]
            existing.auto_renewal = s["auto_renewal"]
            existing.is_fixed = s["is_fixed"]
            existing.is_subscription = s["is_subscription"]
            existing.is_review_target = s["is_review_target"]
            existing.manual_cancel_suggestion = s["manual_cancel_suggestion"]
            existing.auto_cancel_suggestion = s["auto_cancel_suggestion"]
            existing.cancel_suggestion = s["cancel_suggestion"]
            existing.memo = s["memo"]
            continue

        e = Expense(
            id=uuid.uuid4(),
            user_id=DEV_USER_ID,
            name=s["name"],
            category_id=category.id,
            amount=s["amount"],  # 後でDecimalに寄せる前提でOK
            billing_cycle=s["billing_cycle"],
            next_billing_date=s["next_billing_date"],
            auto_renewal=s["auto_renewal"],
            is_fixed=s["is_fixed"],
            is_subscription=s["is_subscription"],
            is_review_target=s["is_review_target"],
            auto_cancel_suggestion=s["auto_cancel_suggestion"],
            manual_cancel_suggestion=s["manual_cancel_suggestion"],
            cancel_suggestion=s["cancel_suggestion"],
            memo=s["memo"],
        )
        db.add(e)

    db.flush()


def main() -> None:
    db = SessionLocal()
    try:
        upsert_dev_user(db)
        upsert_usage_statuses(db)
        categories = upsert_categories(db)
        upsert_expenses(db, categories)
        db.commit()
        print("✅ Seed completed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
