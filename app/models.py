"""
Schedule-ZeroBaran — نماذج Pydantic للتحقق من صحة الطلبات
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerInfo(BaseModel):
    """بيانات العميل عند الحجز."""
    name: str = Field(..., min_length=2, max_length=120, description="اسم العميل")
    email: Optional[EmailStr] = Field(default=None, description="البريد الإلكتروني")
    phone: Optional[str] = Field(default=None, max_length=30)
    telegram_id: Optional[int] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class BookingRequest(BaseModel):
    """طلب حجز موعد جديد."""
    service_id: Optional[str] = None
    start_time: datetime = Field(..., description="وقت بداية الموعد بصيغة ISO 8601")
    customer: CustomerInfo
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("start_time")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        from datetime import datetime as _dt, timezone
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v < _dt.now(timezone.utc):
            raise ValueError("وقت البداية يجب أن يكون في المستقبل")
        return v


class BookingResponse(BaseModel):
    success: bool
    appointment_id: Optional[str] = None
    message: str
    meeting_url: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class AvailabilitySlot(BaseModel):
    """فترة زمنية متاحة للحجز."""
    start_time: str
    end_time: str
    duration_minutes: int
    is_available: bool = True


class AvailabilityResponse(BaseModel):
    date: str
    slots: list[AvailabilitySlot]


class AppointmentUpdate(BaseModel):
    """تحديث حالة موعد."""
    status: Literal["pending", "confirmed", "cancelled", "completed", "no_show"]
    notes: Optional[str] = None
    meeting_url: Optional[str] = None


class WorkingHourRule(BaseModel):
    """قاعدة ساعة عمل أسبوعية."""
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str
    end_time: str
    is_active: bool = True


class ReminderRequest(BaseModel):
    """طلب إرسال تذكير يدوي."""
    appointment_id: str
