#!/usr/bin/env python
"""
Schedule-ZeroBaran — اختبار سريع للاتصال والمكوّنات الأساسية.
يشغّل: فحص الإعدادات، الاتصال بـ Supabase، توليد AI، إرسال تليجرام.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)


def check(label: str, fn):
    print(f"\n— {label} —")
    try:
        result = fn()
        print(f"✅ نجاح: {result}")
        return True
    except Exception as e:
        print(f"❌ فشل: {e}")
        return False


def main() -> int:
    ok = True
    from app.config import settings

    ok &= check("الإعدادات محمّلة", lambda: f"{settings.owner_name} • {settings.owner_email}")

    def check_supabase():
        from app.database import WorkingHoursRepo
        rows = WorkingHoursRepo.list_active()
        return f"{len(rows)} قاعدة ساعات عمل"
    ok &= check("الاتصال بـ Supabase", check_supabase)

    def check_ai():
        from app.ai_brain import AIBrain
        return AIBrain().generate("اكتب كلمة ترحيب واحدة فقط")[:80]
    ok &= check("طبقة الذكاء الاصطناعي", check_ai)

    def check_telegram():
        from app.telegram_bot import TelegramGateway
        tg = TelegramGateway()
        if not tg.token:
            return "تخطّي (لا يوجد توكن)"
        r = tg.notify_owner("🧪 اختبار اتصال من Schedule-ZeroBaran")
        return "تم الإرسال" if r.get("ok") else f"فشل: {r}"
    ok &= check("إشعار تليجرام", check_telegram)

    print("\n" + ("🎉 كل الفحوصات نجحت!" if ok else "⚠️ بعض الفحوصات فشلت — راجع السجل."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
