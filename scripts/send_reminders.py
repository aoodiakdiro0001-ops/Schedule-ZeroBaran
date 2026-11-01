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

from app.reminders import run_reminder_cycle  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("send_reminders")


def main() -> int:
    logger.info("🚀 بدء دورة التذكيرات Schedule-ZeroBaran")
    result = run_reminder_cycle()
    logger.info("📊 النتيجة: %s", json.dumps(result, ensure_ascii=False, indent=2))
    print(f"::set-output name=result::{json.dumps(result, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
