"""解約候補自動判定サービス

判定ルール：
  直近3ヶ月のログが全て「使ってない」(usage_status_id=3) かつ is_skipped=False
  → auto_cancel_suggestion = True

cancel_suggestion の確定ルール：
  manual_cancel_suggestion が None でない → manual の値を優先
  manual_cancel_suggestion が None       → auto_cancel_suggestion の値を使う
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.usage_log import UsageLog

UNUSED_STATUS_ID = 3  # 「使ってない」のID
CONSECUTIVE_MONTHS = 3  # 何ヶ月連続で判定するか


def recalculate_cancel_suggestion(expense_id: uuid.UUID, db: Session) -> None:
    """
    指定Expenseの解約候補フラグを再計算して保存する。
    usage_log 登録・更新時に呼び出す。
    """
    expense = db.get(Expense, expense_id)
    if not expense or expense.deleted_at is not None:
        return

    # 解約候補判定対象でなければスキップ
    if not expense.is_review_target:
        return

    # 直近N件のログを取得（月の降順）
    recent_logs = (
        db.execute(
            select(UsageLog)
            .where(UsageLog.expense_id == expense_id)
            .where(UsageLog.is_skipped.is_(False))
            .order_by(UsageLog.month.desc())
            .limit(CONSECUTIVE_MONTHS)
        )
        .scalars()
        .all()
    )

    # N件揃っていて全部「使ってない」なら auto=True
    auto = (
        len(recent_logs) >= CONSECUTIVE_MONTHS
        and all(log.usage_status_id == UNUSED_STATUS_ID for log in recent_logs)
    )

    expense.auto_cancel_suggestion = auto

    # cancel_suggestion の確定：manual が設定されていれば優先
    if expense.manual_cancel_suggestion is not None:
        expense.cancel_suggestion = expense.manual_cancel_suggestion
    else:
        expense.cancel_suggestion = auto

    # 理由テキストを自動生成（表示用）
    if auto:
        expense.cancel_suggestion_reason = f"{CONSECUTIVE_MONTHS}ヶ月連続で使用していません"
    elif expense.cancel_suggestion_reason and not expense.manual_cancel_suggestion:
        expense.cancel_suggestion_reason = None
