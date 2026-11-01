"""
Schedule-ZeroBaran — محرك الجدولة الذكي
يحسب الفترات المتاحة، يكتشف التعارض، ويُثبت الحجوزات بأمان.
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

from datetime import date as Date, datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from .config import settings
from .database import (
    AppointmentsRepo,
    ScheduleExceptionsRepo,
    ServicesRepo,
    WorkingHoursRepo,
)


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


def now_local() -> datetime:
    return datetime.now(_tz())


# ===== حساب الفترات المتاحة =====
def get_available_slots(target_date: Date, service_id: Optional[str] = None) -> list[dict]:
    """
    يُرجع قائمة الفترات المتاحة في تاريخ معيّن بناءً على:
      1. ساعات العمل لهذا اليوم.
      2. الاستثناءات (إجازات/أعياد).
      3. المواعيد المحجوزة مسبقاً (مع منع التداخل).
      4. مدة الخدمة المختارة.
    """
    # 1) التحقق من الاستثناءات
    iso_date = target_date.isoformat()
    exceptions = ScheduleExceptionsRepo.list_between(iso_date, iso_date)
    if iso_date in exceptions:
        return []

    # 2) ساعات العمل لهذا اليوم
    day_of_week = target_date.weekday()  # 0=الإثنين ... 6=الأحد (Python)
    # قاعدة البيانات: 0=الأحد ... 6=السبت
    db_day = (day_of_week + 1) % 7
    working_hours = [w for w in WorkingHoursRepo.list_active() if w["day_of_week"] == db_day]
    if not working_hours:
        return []

    # 3) مدة الجلسة
    duration = settings.session_duration_minutes
    if service_id:
        service = ServicesRepo.get(service_id)
        if service:
            duration = service.get("duration_minutes", duration)

    # 4) المواعيد المحجوزة في هذا اليوم
    day_start = datetime.combine(target_date, time(0, 0), tzinfo=_tz())
    day_end = day_start + timedelta(days=1)
    booked = AppointmentsRepo.list_between(
        day_start.isoformat(), day_end.isoformat(), statuses=["pending", "confirmed"]
    )

    # تحويل المواعيد المحجوزة إلى فترات (UTC-aware)
    busy_intervals = []
    for appt in booked:
        s = _parse_dt(appt["start_time"])
        e = _parse_dt(appt["end_time"])
        busy_intervals.append((s, e))
    busy_intervals.sort(key=lambda x: x[0])

    # 5) توليد الفترات المتاحة
    slots: list[dict] = []
    for wh in working_hours:
        sh, sm = map(int, wh["start_time"].split(":"))
        eh, em = map(int, wh["end_time"].split(":"))
        slot_start = day_start.replace(hour=sh, minute=sm, second=0, microsecond=0)
        slot_end = day_start.replace(hour=eh, minute=em, second=0, microsecond=0)

        # لا نعرض المواعيد الماضية إذا كان اليوم هو اليوم الحالي
        now = now_local()
        if slot_start < now:
            slot_start = now.replace(second=0, microsecond=0)
            # تقريب للأعلى لأقرب 15 دقيقة
            minute = ((slot_start.minute // 15) + 1) * 15
            slot_start = slot_start.replace(minute=0) + timedelta(minutes=minute)
        if slot_start >= slot_end:
            continue

        # تقسيم الفترة إلى خانات بحسب المدة
        cursor = slot_start
        while cursor + timedelta(minutes=duration) <= slot_end:
            slot_finish = cursor + timedelta(minutes=duration)
            # فحص التعارض
            conflict = any(
                not (slot_finish <= b_start or cursor >= b_end)
                for b_start, b_end in busy_intervals
            )
            if not conflict:
                slots.append({
                    "start_time": cursor.isoformat(),
                    "end_time": slot_finish.isoformat(),
                    "duration_minutes": duration,
                    "is_available": True,
                })
            cursor += timedelta(minutes=duration)

    return slots


def get_availability_for_days(num_days: Optional[int] = None) -> list[dict]:
    """يُرجع الإتاحة لعدد أيام قادمة (افتراضياً AVAILABILITY_WINDOW_DAYS)."""
    days = num_days or settings.availability_window_days
    today = now_local().date()
    result = []
    for i in range(days):
        d = today + timedelta(days=i)
        slots = get_available_slots(d)
        if slots:
            result.append({
                "date": d.isoformat(),
                "weekday": _weekday_ar(d.weekday()),
                "slots": slots,
                "slots_count": len(slots),
            })
    return result


# ===== التحقق من التعارض والحجز =====
def is_slot_available(start_time: datetime, duration_minutes: int) -> bool:
    """يفحص إن كانت الفترة الزمنية حرة فعلاً (لتفادي التعارض المتزامن)."""
    end_time = start_time + timedelta(minutes=duration_minutes)
    # نوّع المدة بأخذ اليوم بالكامل للبحث
    day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    booked = AppointmentsRepo.list_between(
        day_start.isoformat(), day_end.isoformat(), statuses=["pending", "confirmed"]
    )
    for appt in booked:
        b_start = _parse_dt(appt["start_time"])
        b_end = _parse_dt(appt["end_time"])
        if not (end_time <= b_start or start_time >= b_end):
            return False
    return True


def create_appointment(
    start_time: datetime,
    customer: dict,
    service_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """
    يُنشئ موعداً جديداً بعد فحص التعارض بدقة.
    يُرجع قاموساً يحوي تفاصيل الموعد أو يطلق استثناء عند التعارض.
    """
    # مدة الجلسة
    duration = settings.session_duration_minutes
    service_name = None
    if service_id:
        service = ServicesRepo.get(service_id)
        if service:
            duration = service.get("duration_minutes", duration)
            service_name = service.get("name")
    end_time = start_time + timedelta(minutes=duration)

    # فحص التعارض النهائي
    if not is_slot_available(start_time, duration):
        raise ValueError("⚠️ هذه الفترة محجوزة بالفعل أو متداخلة مع موعد آخر. اختر وقتاً آخر.")

    # بناء الحمولة
    payload = {
        "customer_name": customer["name"],
        "customer_email": customer.get("email"),
        "customer_phone": customer.get("phone"),
        "customer_telegram_id": customer.get("telegram_id"),
        "service_id": service_id,
        "service_name": service_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": "confirmed",  # تأكيد فوري (يمكن تغييره إلى pending)
        "meeting_url": settings.default_meeting_url,
        "notes": notes,
        "reminder_sent": False,
    }
    return AppointmentsRepo.create(payload)


# ===== أدوات مساعدة =====
def _parse_dt(value) -> datetime:
    """يحلّ قيمة تاريخ لـ datetime مع منطقة زمنية."""
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_tz())
    return dt


def _weekday_ar(idx: int) -> str:
    """يُرجع اسم اليوم بالعربية."""
    names = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    return names[idx % 7]


def format_appointment_for_owner(appt: dict) -> str:
    """يُنسّق موعداً كرسالة تُرسل للمالك عبر تليجرام."""
    start = _parse_dt(appt["start_time"]).astimezone(_tz())
    end = _parse_dt(appt["end_time"]).astimezone(_tz())
    return (
        f"📅 <b>موعد جديد مؤكد</b>\n\n"
        f"👤 <b>العميل:</b> {appt.get('customer_name','—')}\n"
        f"💼 <b>الخدمة:</b> {appt.get('service_name') or 'استشارة عامة'}\n"
        f"⏰ <b>الوقت:</b> {start.strftime('%Y-%m-%d • %H:%M')} — {end.strftime('%H:%M')}\n"
        f"📧 <b>البريد:</b> {appt.get('customer_email') or '—'}\n"
        f"📱 <b>الهاتف:</b> {appt.get('customer_phone') or '—'}\n"
        f"🔗 <b>رابط اللقاء:</b> {appt.get('meeting_url') or '—'}\n"
        f"📝 <b>ملاحظات:</b> {appt.get('notes') or '—'}\n\n"
        f"<i>تم التأكيد آلياً بواسطة Schedule-ZeroBaran</i>"
    )


def format_appointment_for_customer(appt: dict, business_name: str) -> str:
    """رسالة التأكيد التي تُرسل للعميل."""
    start = _parse_dt(appt["start_time"]).astimezone(_tz())
    end = _parse_dt(appt["end_time"]).astimezone(_tz())
    return (
        f"✅ <b>تم تأكيد موعدك بنجاح!</b>\n\n"
        f"🏢 <b>{business_name}</b>\n\n"
        f"💼 <b>الخدمة:</b> {appt.get('service_name') or 'استشارة عامة'}\n"
        f"⏰ <b>الموعد:</b> {start.strftime('%Y-%m-%d • %H:%M')} — {end.strftime('%H:%M')}\n"
        f"🔗 <b>رابط اللقاء:</b> {appt.get('meeting_url') or 'سيتم إرساله لاحقاً'}\n\n"
        f"📞 للاستفسار أو إعادة الجدولة، تواصل معنا.\n\n"
        f"<i>تذكير: ستصل لك رسالة تذكير قبل الموعد بقليل.</i>"
    )


def format_reminder_for_customer(appt: dict, business_name: str, lead_hours: int) -> str:
    """رسالة تذكير قبل الموعد."""
    start = _parse_dt(appt["start_time"]).astimezone(_tz())
    return (
        f"⏰ <b>تذكير بموعدك القادم</b>\n\n"
        f"🏢 <b>{business_name}</b>\n\n"
        f"💼 <b>الخدمة:</b> {appt.get('service_name') or 'استشارة عامة'}\n"
        f"⏰ <b>الموعد:</b> {start.strftime('%Y-%m-%d • %H:%M')}\n"
        f"🔗 <b>رابط اللقاء:</b> {appt.get('meeting_url') or '—'}\n\n"
        f"<i>يبدأ موعدك خلال {lead_hours} ساعة. كن على الموعد من فضلك.</i>"
    )
