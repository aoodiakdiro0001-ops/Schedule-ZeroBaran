#!/usr/bin/env python
"""
Schedule-ZeroBaran — سكربت تنظيف المواعيد المنتهية
يُشغّل يومياً لتحديث حالة المواعيد المنتهية إلى 'completed'.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import logging
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from app.config import settings  # noqa: E402
from app.reminders import mark_expired_appointments  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("cleanup")


def main() -> int:
    logger.info("🧹 بدء تنظيف المواعيد المنتهية")

    # Same guard as send_reminders.py: no credentials -> skip, don't fail.
    if not settings.is_supabase_ready:
        logger.warning(
            "⚠️ Supabase غير مُعد (SUPABASE_URL / SUPABASE_KEY فارغة). "
            "تخطّي التنظيف — أضف الأسرار لتفعيله."
        )
        return 0

    count = mark_expired_appointments()
    logger.info("✅ تم تحديث %d موعد", count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
