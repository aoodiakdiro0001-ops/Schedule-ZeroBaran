"""
Schedule-ZeroBaran — نقطة دخول Vercel Serverless
يجعل تطبيق FastAPI يعمل كـ Serverless Function على Vercel.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import os
import sys

# ضمان أن جذر المشروع في المسار لاستيراد حزمة app
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app  # noqa: E402

# تصدير معالج Vercel
handler = app
