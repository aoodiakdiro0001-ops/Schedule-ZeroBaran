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

from app.reminders import mark_expired_appointments  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("cleanup")


def main() -> int:
    logger.info("🧹 بدء تنظيف المواعيد المنتهية")
    count = mark_expired_appointments()
    logger.info("✅ تم تحديث %d موعد", count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
