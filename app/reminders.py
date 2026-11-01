"""
Schedule-ZeroBaran — محرك التذكيرات الذكي
يفحص المواعيد القادمة ويُرسل تذكيرات تلقائية قبل الموعد.
يُشغّل عبر GitHub Actions أو APScheduler.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import settings
from .database import AppointmentsRepo
from .scheduler import _parse_dt, format_reminder_for_customer
from .telegram_bot import TelegramGateway

logger = logging.getLogger(__name__)

# كم ساعة قبل الموعد نُرسل التذكير؟
REMINDER_LEAD_HOURS = 1


def send_due_reminders(lead_hours: int = REMINDER_LEAD_HOURS) -> int:
    """
    يفحص جميع المواعيد المؤكدة التي لم تُذكَّر بعد،
    ويُرسل تذكيراً لكل موعد يبدأ خلال `lead_hours` ساعة قادمة.
    يُرجع عدد التذكيرات المُرسلة.
    """
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    window_end = (now + timedelta(hours=lead_hours)).isoformat()

    pending = AppointmentsRepo.list_pending_reminders(window_end)
    if not pending:
        logger.info("ℹ️ لا توجد تذكيرات مستحقة الآن.")
        return 0

    tg = TelegramGateway()
    sent_count = 0

    for appt in pending:
        start_dt = _parse_dt(appt["start_time"]).astimezone(tz)
        # نُذكّر فقط المواعيد المستقبلية ضمن النافذة
        if start_dt <= now:
            continue
        if (start_dt - now).total_seconds() > lead_hours * 3600:
            continue

        # التذكير عبر تليجرام للعميل
        text = format_reminder_for_customer(
            appt, settings.owner_business_name, lead_hours
        )
        result = tg.notify_customer(
            telegram_id=appt.get("customer_telegram_id"),
            text=text,
            appointment_id=appt.get("id"),
        )
        if result.get("ok"):
            AppointmentsRepo.mark_reminder_sent(appt["id"])
            sent_count += 1
            logger.info("✅ تذكير مُرسل للموعد %s (العميل: %s)",
                        appt["id"], appt.get("customer_name"))
        else:
            logger.warning("⚠️ تعذّر إرسال التذكير للموعد %s", appt["id"])

    return sent_count


def mark_expired_appointments() -> int:
    """
    يحدّث حالة المواعيد المنتهية إلى 'completed'.
    يُرجع عدد المواعيد المُحدّثة.
    """
    expired = AppointmentsRepo.list_expired_pending()
    if not expired:
        return 0
    for appt in expired:
        AppointmentsRepo.update(appt["id"], {"status": "completed"})
    logger.info("🔄 تم تحديث %d موعد منتهٍ إلى 'completed'", len(expired))
    return len(expired)


def run_reminder_cycle() -> dict:
    """دورة كاملة: تذكيرات + تنظيف منتهي."""
    reminders = send_due_reminders()
    completed = mark_expired_appointments()
    return {
        "reminders_sent": reminders,
        "appointments_completed": completed,
        "run_at": datetime.now(ZoneInfo(settings.timezone)).isoformat(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
    result = run_reminder_cycle()
    print("📊 نتائج الدورة:", result)
