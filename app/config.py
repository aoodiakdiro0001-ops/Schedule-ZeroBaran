"""
Schedule-ZeroBaran — إعدادات المنظومة المركزية
يقرأ جميع المتغيرات من البيئة / ملف .env
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """الإعدادات المركزية للمنظومة."""

    @model_validator(mode="before")
    @classmethod
    def _blank_env_is_unset(cls, data):
        # GitHub Actions exports every unset secret as an EMPTY string ("").
        # pydantic-settings prefers the env value over the Field default, so
        # AI_PROVIDER="" / SESSION_DURATION_MINUTES="" raise ValidationError and
        # the whole cron job dies before doing any work. Drop blank values from
        # the incoming mapping so the declared defaults apply instead.
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if not (isinstance(v, str) and not v.strip())}
        return data

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== Supabase =====
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")
    supabase_service_key: str = Field(default="", alias="SUPABASE_SERVICE_KEY")

    # ===== AI Providers =====
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    ai_provider: Literal["gemini", "groq"] = Field(
        default="gemini", alias="AI_PROVIDER"
    )

    # ===== Telegram =====
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_owner_chat_id: str = Field(default="", alias="TELEGRAM_OWNER_CHAT_ID")
    default_meeting_url: str = Field(
        default="https://meet.google.com/", alias="DEFAULT_MEETING_URL"
    )

    # ===== General =====
    timezone: str = Field(default="Europe/Istanbul", alias="TIMEZONE")
    session_duration_minutes: int = Field(default=60, alias="SESSION_DURATION_MINUTES")
    availability_window_days: int = Field(default=14, alias="AVAILABILITY_WINDOW_DAYS")
    port: int = Field(default=8000, alias="PORT")

    # ===== Owner Info =====
    owner_name: str = Field(default="Baran Avisat", alias="OWNER_NAME")
    owner_email: str = Field(default="Baranavisat@gmail.com", alias="OWNER_EMAIL")
    owner_whatsapp: str = Field(default="00905313263722", alias="OWNER_WHATSAPP")
    owner_business_name: str = Field(
        default="Schedule-ZeroBaran Smart Office", alias="OWNER_BUSINESS_NAME"
    )

    @property
    def supabase_admin_key(self) -> str:
        """يُرجع مفتاح الخدمة إن وُجد، وإلا المفتاح العادي."""
        return self.supabase_service_key or self.supabase_key

    @property
    def is_supabase_ready(self) -> bool:
        """True only when both Supabase coordinates are actually present.

        GitHub Actions exports every unset secret as "", so this must be
        checked before touching the database — otherwise the hourly cron
        raises RuntimeError and stays permanently red on a repo where the
        secrets were never configured.
        """
        return bool(self.supabase_url and self.supabase_admin_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """مخبأ (cached) للإعدادات لتفادي القراءة المتكررة."""
    return Settings()


# نسخة عامة للاستيراد السهل
settings = get_settings()
