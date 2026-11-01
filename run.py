"""
Schedule-ZeroBaran — مساعد التشغيل الموحّد
يوفّر أوامر بسيطة لإدارة المنظومة محلياً:

  python run.py api         — تشغيل الـ API
  python run.py dashboard   — تشغيل لوحة التحكم
  python run.py booking     — تشغيل واجهة الحجز
  python run.py bot         — تشغيل بوت تليجرام
  python run.py reminders   — تشغيل دورة تذكيرات
  python run.py cleanup     — تنظيف المواعيد المنتهية
  python run.py seed        — زرع بيانات أولية
  python run.py health      — فحص سلامة المكوّنات

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd: list[str]) -> int:
    print(f"▶️  تشغيل: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=HERE)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    action = sys.argv[1].lower()

    if action == "api":
        return run([
            sys.executable, "-m", "uvicorn",
            "app.main:app", "--reload", "--port", "8000",
        ])
    if action == "dashboard":
        return run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])
    if action == "booking":
        return run([sys.executable, "-m", "streamlit", "run", "booking_ui/app.py"])
    if action == "bot":
        return run([sys.executable, "-m", "app.telegram_bot"])
    if action == "reminders":
        return run([sys.executable, "scripts/send_reminders.py"])
    if action == "cleanup":
        return run([sys.executable, "scripts/cleanup_appointments.py"])
    if action == "seed":
        return run([sys.executable, "scripts/seed_data.py"])
    if action == "health":
        return run([sys.executable, "scripts/health_check.py"])

    print(f"❌ أمر غير معروف: {action}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
