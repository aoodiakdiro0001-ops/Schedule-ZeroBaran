#!/usr/bin/env python
"""
Schedule-ZeroBaran — سكربت إرسال التذكيرات
يُشغّل عبر GitHub Actions كل ساعة لإرسال التذكيرات وتحديث المواعيد المنتهية.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import json
import logging
import os
import sys

# ضمان إمكانية الاستيراد من جذر المشروع
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from app.config import settings  # noqa: E402
from app.reminders import run_reminder_cycle  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("send_reminders")


def main() -> int:
    logger.info("🚀 بدء دورة التذكيرات Schedule-ZeroBaran")

    # Missing Supabase credentials are a configuration state, not a defect.
    # GitHub Actions exports every unset secret as "", so a fresh clone used
    # to raise RuntimeError from get_supabase() and keep this cron red
    # forever. Report honestly and exit 0 until the secrets exist.
    if not settings.is_supabase_ready:
        logger.warning(
            "⚠️ Supabase غير مُعد (SUPABASE_URL / SUPABASE_KEY فارغة). "
            "تخطّي دورة التذكيرات — أضف الأسرار لتفعيلها."
        )
        return 0

    result = run_reminder_cycle()
    logger.info("📊 النتيجة: %s", json.dumps(result, ensure_ascii=False, indent=2))
    print(f"::set-output name=result::{json.dumps(result, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
