"""
Schedule-ZeroBaran — طبقة الاتصال بقاعدة بيانات Supabase
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional

from supabase import Client, create_client

from .config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """يُرجع نسخة موحّدة من عميل Supabase."""
    if not settings.supabase_url or not settings.supabase_admin_key:
        raise RuntimeError(
            "❌ إعدادات Supabase غير مكتملة. راجع ملف .env وتأكد من SUPABASE_URL و SUPABASE_KEY"
        )
    return create_client(settings.supabase_url, settings.supabase_admin_key)


# ===== واجهات الجداول =====
class WorkingHoursRepo:
    """إدارة ساعات العمل الأسبوعية."""

    @staticmethod
    def list_active() -> list[dict[str, Any]]:
        supabase = get_supabase()
        resp = (
            supabase.table("working_hours")
            .select("*")
            .eq("is_active", True)
            .order("day_of_week")
            .order("start_time")
            .execute()
        )
        return resp.data or []

    @staticmethod
    def upsert(rows: list[dict[str, Any]]) -> None:
        supabase = get_supabase()
        supabase.table("working_hours").upsert(rows, on_conflict="day_of_week,start_time,end_time").execute()


class ScheduleExceptionsRepo:
    """إدارة الاستثناءات (عطل/إجازات)."""

    @staticmethod
    def list_between(start_date: str, end_date: str) -> list[str]:
        supabase = get_supabase()
        resp = (
            supabase.table("schedule_exceptions")
            .select("exception_date")
            .gte("exception_date", start_date)
            .lte("exception_date", end_date)
            .execute()
        )
        return [r["exception_date"] for r in (resp.data or [])]

    @staticmethod
    def add(date: str, reason: str = "") -> None:
        supabase = get_supabase()
        supabase.table("schedule_exceptions").upsert(
            {"exception_date": date, "reason": reason}, on_conflict="exception_date"
        ).execute()


class ServicesRepo:
    """إدارة الخدمات المعروضة."""

    @staticmethod
    def list_active() -> list[dict[str, Any]]:
        supabase = get_supabase()
        resp = (
            supabase.table("services")
            .select("*")
            .eq("is_active", True)
            .order("name")
            .execute()
        )
        return resp.data or []

    @staticmethod
    def get(service_id: str) -> Optional[dict[str, Any]]:
        supabase = get_supabase()
        resp = supabase.table("services").select("*").eq("id", service_id).single().execute()
        return resp.data


class CustomersRepo:
    """إدارة بيانات العملاء."""

    @staticmethod
    def upsert(customer: dict[str, Any]) -> dict[str, Any]:
        supabase = get_supabase()
        resp = supabase.table("customers").upsert(
            customer, on_conflict="telegram_id"
        ).execute()
        return (resp.data or [{}])[0]

    @staticmethod
    def get_by_telegram_id(telegram_id: int) -> Optional[dict[str, Any]]:
        supabase = get_supabase()
        resp = (
            supabase.table("customers")
            .select("*")
            .eq("telegram_id", telegram_id)
            .limit(1)
            .execute()
        )
        return (resp.data or [None])[0]


class AppointmentsRepo:
    """إدارة المواعيد — الجدول المحوري للمنظومة."""

    @staticmethod
    def list_between(start: str, end: str, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        statuses = statuses or ["pending", "confirmed"]
        supabase = get_supabase()
        q = (
            supabase.table("appointments")
            .select("*")
            .gte("start_time", start)
            .lte("start_time", end)
            .in_("status", statuses)
            .order("start_time")
        )
        resp = q.execute()
        return resp.data or []

    @staticmethod
    def get(appointment_id: str) -> Optional[dict[str, Any]]:
        supabase = get_supabase()
        resp = supabase.table("appointments").select("*").eq("id", appointment_id).single().execute()
        return resp.data

    @staticmethod
    def create(payload: dict[str, Any]) -> dict[str, Any]:
        supabase = get_supabase()
        resp = supabase.table("appointments").insert(payload).execute()
        return (resp.data or [{}])[0]

    @staticmethod
    def update(appointment_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        supabase = get_supabase()
        resp = (
            supabase.table("appointments")
            .update(patch)
            .eq("id", appointment_id)
            .execute()
        )
        return (resp.data or [{}])[0]

    @staticmethod
    def mark_reminder_sent(appointment_id: str) -> None:
        supabase = get_supabase()
        supabase.table("appointments").update({"reminder_sent": True}).eq("id", appointment_id).execute()

    @staticmethod
    def list_pending_reminders(window_end: str) -> list[dict[str, Any]]:
        """المواعيد المؤكدة التي تحتاج تذكيراً قبل window_end."""
        supabase = get_supabase()
        resp = (
            supabase.table("appointments")
            .select("*")
            .eq("reminder_sent", False)
            .in_("status", ["confirmed", "pending"])
            .lte("start_time", window_end)
            .order("start_time")
            .execute()
        )
        return resp.data or []

    @staticmethod
    def list_expired_pending() -> list[dict[str, Any]]:
        """المواعيد المنتهية الصلاحية التي لم تُحدّث حالتها."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        supabase = get_supabase()
        resp = (
            supabase.table("appointments")
            .select("*")
            .lt("end_time", now_iso)
            .in_("status", ["pending", "confirmed"])
            .order("end_time")
            .execute()
        )
        return resp.data or []


class NotificationsLogRepo:
    """سجل الإشعارات المُرسلة."""

    @staticmethod
    def add(entry: dict[str, Any]) -> None:
        supabase = get_supabase()
        supabase.table("notifications_log").insert(entry).execute()
