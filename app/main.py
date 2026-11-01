"""
Schedule-ZeroBaran — التطبيق الرئيسي (FastAPI)
نقطة الدخول للمحرك المنطقي. يوفّر REST API كاملاً
للحجز، الإتاحة، إدارة المواعيد، والتذكيرات.

المؤلف: Baran Avisan (Baranavisat@gmail.com)
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import date as Date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import (
    AppointmentsRepo,
    ServicesRepo,
    WorkingHoursRepo,
    ScheduleExceptionsRepo,
)
from .models import (
    AppointmentUpdate,
    AvailabilityResponse,
    BookingRequest,
    BookingResponse,
    WorkingHourRule,
)
from .scheduler import (
    create_appointment,
    format_appointment_for_customer,
    format_appointment_for_owner,
    get_available_slots,
    get_availability_for_days,
)
from .telegram_bot import TelegramGateway
from .ai_brain import craft_confirmation_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger("schedule-zerobaran")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Schedule-ZeroBaran يبدأ التشغيل...")
    logger.info("👤 المالك: %s | 📧 %s", settings.owner_name, settings.owner_email)
    yield
    logger.info("🛑 Schedule-ZeroBaran توقف.")


app = FastAPI(
    title="Schedule-ZeroBaran API",
    description=(
        "منظومة ذاتية ذكية لحجز المواعيد، الجدولة، وإدارة الأجندة — "
        "مبنية بالكامل بموارد مجانية. © Baran Avisat"
    ),
    version="1.0.0",
    contact={
        "name": "Baran Avisat",
        "email": "Baranavisat@gmail.com",
        "url": "https://wa.me/905313263722",
    },
    lifespan=lifespan,
)

# CORS — السماح للواجهات (Streamlit / Web) بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# نقاط النهاية الأساسية
# ============================================================

@app.get("/")
def root():
    """الصفحة الرئيسية — معلومات المنظومة."""
    return {
        "name": "Schedule-ZeroBaran",
        "version": "1.0.0",
        "tagline": "المنظومة الذاتية الذكية لحجز المواعيد والجدولة",
        "author": "Baran Avisat",
        "email": settings.owner_email,
        "whatsapp": settings.owner_whatsapp,
        "endpoints": [
            "/health",
            "/api/services",
            "/api/availability",
            "/api/availability/{date}",
            "/api/book",
            "/api/appointments",
            "/api/appointments/{id}",
            "/api/working-hours",
            "/api/reminders/run",
        ],
    }


@app.get("/health")
def health():
    """فحص حيوية الخدمة."""
    return {"status": "ok", "service": "schedule-zerobaran", "tz": settings.timezone}


# ============================================================
# الإتاحة (Availability)
# ============================================================

@app.get("/api/services")
def list_services():
    """يُرجع قائمة الخدمات النشطة."""
    return {"services": ServicesRepo.list_active()}


@app.get("/api/availability")
def list_availability(days: int = Query(default=7, ge=1, le=60)):
    """يُرجع الفترات المتاحة لعدد أيام قادمة."""
    return {"availability": get_availability_for_days(days)}


@app.get("/api/availability/{target_date}")
def availability_for_date(target_date: str, service_id: Optional[str] = None):
    """يُرجع الفترات المتاحة في تاريخ معيّن (YYYY-MM-DD)."""
    try:
        d = Date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(400, "صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD")
    slots = get_available_slots(d, service_id=service_id)
    return AvailabilityResponse(date=target_date, slots=slots)


# ============================================================
# الحجز (Booking)
# ============================================================

@app.post("/api/book", response_model=BookingResponse)
def book_appointment(req: BookingRequest):
    """حجز موعد جديد مع فحص التعارض والتأكيد الفوري."""
    try:
        appt = create_appointment(
            start_time=req.start_time,
            customer=req.customer.model_dump(),
            service_id=req.service_id,
            notes=req.notes,
        )
    except ValueError as e:
        raise HTTPException(409, str(e))
    except Exception as e:
        logger.exception("❌ خطأ أثناء الحجز")
        raise HTTPException(500, f"خطأ داخلي: {e}")

    # إشعار المالك فوراً
    tg = TelegramGateway()
    tg.notify_owner(format_appointment_for_owner(appt))

    # محاولة توليد رسالة تأكيد مخصصة عبر AI
    try:
        confirmation = craft_confirmation_message(
            customer_name=req.customer.name,
            service_name=appt.get("service_name") or "استشارة عامة",
            start_time=appt["start_time"],
            meeting_url=appt.get("meeting_url") or "—",
        )
        AppointmentsRepo.update(appt["id"], {"confirmation_message": confirmation})
    except Exception as e:
        logger.warning("تعذّر توليد رسالة AI: %s", e)
        confirmation = format_appointment_for_customer(appt, settings.owner_business_name)

    # إرسال تأكيد للعميل عبر تليجرام إن أمكن
    tg.notify_customer(
        telegram_id=req.customer.telegram_id,
        text=confirmation,
        appointment_id=appt.get("id"),
    )

    return BookingResponse(
        success=True,
        appointment_id=appt.get("id"),
        message="تم تأكيد حجزك بنجاح! ستصل تذكيرات قبل الموعد.",
        meeting_url=appt.get("meeting_url"),
        start_time=appt.get("start_time"),
        end_time=appt.get("end_time"),
    )


# ============================================================
# إدارة المواعيد
# ============================================================

@app.get("/api/appointments")
def list_appointments(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
):
    """يُرجع قائمة المواعيد خلال فترة."""
    statuses = [status] if status else ["pending", "confirmed", "completed", "cancelled", "no_show"]
    start = from_date or datetime.now().isoformat()
    end = to_date or (datetime.now() + timedelta(days=30)).isoformat()
    items = AppointmentsRepo.list_between(start, end, statuses=statuses)
    return {"appointments": items, "count": len(items)}


@app.get("/api/appointments/{appointment_id}")
def get_appointment(appointment_id: str):
    appt = AppointmentsRepo.get(appointment_id)
    if not appt:
        raise HTTPException(404, "الموعد غير موجود")
    return appt


@app.patch("/api/appointments/{appointment_id}")
def update_appointment(appointment_id: str, patch: AppointmentUpdate):
    update_data = patch.model_dump(exclude_none=True)
    updated = AppointmentsRepo.update(appointment_id, update_data)
    return {"success": True, "appointment": updated}


@app.post("/api/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: str):
    AppointmentsRepo.update(appointment_id, {"status": "cancelled"})
    return {"success": True, "message": "تم إلغاء الموعد"}


# ============================================================
# إدارة ساعات العمل
# ============================================================

@app.get("/api/working-hours")
def list_working_hours():
    return {"working_hours": WorkingHoursRepo.list_active()}


@app.post("/api/working-hours")
def set_working_hours(rules: list[WorkingHourRule]):
    rows = [r.model_dump() for r in rules]
    WorkingHoursRepo.upsert(rows)
    return {"success": True, "count": len(rows)}


@app.post("/api/schedule-exceptions")
def add_exception(date: str, reason: str = ""):
    ScheduleExceptionsRepo.add(date, reason)
    return {"success": True, "date": date, "reason": reason}


# ============================================================
# التذكيرات اليدوية
# ============================================================

@app.post("/api/reminders/run")
def trigger_reminders():
    """يُشغّل دورة تذكيرات يدوياً (مفيد للاختبار)."""
    from .reminders import run_reminder_cycle
    result = run_reminder_cycle()
    return result


@app.post("/api/cleanup")
def trigger_cleanup():
    """يشغّل تنظيف المواعيد المنتهية."""
    from .reminders import mark_expired_appointments
    return {"completed": mark_expired_appointments()}


# ============================================================
# التشغيل المباشر
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="info",
    )
