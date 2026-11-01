#!/usr/bin/env python
"""
Schedule-ZeroBaran — سكربت أولي لزرع بيانات تجريبية في Supabase.
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import logging
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from app.database import (  # noqa: E402
    ServicesRepo,
    WorkingHoursRepo,
    ScheduleExceptionsRepo,
    get_supabase,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger("seed")


def seed() -> None:
    logger.info("🌱 زرع ساعات العمل الافتراضية...")
    WorkingHoursRepo.upsert([
        {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "is_active": True},
        {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00", "is_active": True},
        {"day_of_week": 3, "start_time": "09:00", "end_time": "17:00", "is_active": True},
        {"day_of_week": 4, "start_time": "09:00", "end_time": "17:00", "is_active": True},
        {"day_of_week": 5, "start_time": "09:00", "end_time": "17:00", "is_active": True},
    ])

    logger.info("🌱 زرع الخدمات الافتراضية...")
    supabase = get_supabase()
    supabase.table("services").upsert(
        [
            {"name": "استشارة عامة", "description": "جلسة استشارية مدتها ساعة", "duration_minutes": 60, "price": 0, "is_active": True},
            {"name": "جلسة متابعة", "description": "جلسة متابعة 30 دقيقة", "duration_minutes": 30, "price": 0, "is_active": True},
            {"name": "اجتماع عمل", "description": "اجتماع 45 دقيقة", "duration_minutes": 45, "price": 0, "is_active": True},
        ],
        on_conflict="name",
    ).execute()

    logger.info("✅ اكتملت زراعة البيانات الأولية.")


if __name__ == "__main__":
    seed()
