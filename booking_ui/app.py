"""
Schedule-ZeroBaran — واجهة حجز العميل (Booking UI)
صفحة عامة بسيطة يفتحها العميل لحجز موعد بضغطة زر.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import settings  # noqa: E402

st.set_page_config(
    page_title="احجز موعدك — Schedule-ZeroBaran",
    page_icon="🗓️",
    layout="centered",
)

# تنسيقات RTL وقلوب أجمل
st.markdown("""
<style>
    .main .block-container { direction: rtl; max-width: 720px; padding-top: 2rem; }
    h1, h2, h3 { text-align: center !important; }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        padding: 0.6rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338ca, #6d28d9);
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ====== رأس الصفحة ======
st.markdown(f"""
# 🗓️ احجز موعدك مع {settings.owner_business_name}

مرحباً بك! اختر الخدمة المناسبة والوقت المتاح، وسيتم تأكيد حجزك فوراً.
ستصلك رسالة تأكيد وتذكير قبل الموعد. ✨
""")

# عنوان API (يمكن أن يكون محلياً أو منشوراً)
API_URL = os.environ.get("API_URL", f"http://localhost:{settings.port}")


@st.cache_data(ttl=60)
def fetch_services():
    try:
        r = httpx.get(f"{API_URL}/api/services", timeout=10)
        r.raise_for_status()
        return r.json().get("services", [])
    except Exception as e:
        st.error(f"تعذّر جلب الخدمات: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_availability(days: int = 7):
    try:
        r = httpx.get(f"{API_URL}/api/availability", params={"days": days}, timeout=15)
        r.raise_for_status()
        return r.json().get("availability", [])
    except Exception as e:
        st.error(f"تعذّر جلب الإتاحة: {e}")
        return []


# ====== الخطوة 1: اختيار الخدمة ======
services = fetch_services()
if not services:
    st.warning("لا توجد خدمات متاحة حالياً. حاول لاحقاً.")
    st.stop()

service_names = {s["id"]: s["name"] for s in services}
service_id = st.selectbox(
    "1️⃣ اختر الخدمة",
    options=list(service_names.keys()),
    format_func=lambda x: service_names[x],
)

# ====== الخطوة 2: عرض الأوقات المتاحة ======
st.markdown("### 2️⃣ اختر الوقت المناسب")
avail = fetch_availability(7)
if not avail:
    st.info("لا توجد أوقات متاحة حالياً.")
    st.stop()

# بناء قائمة (label, value)
slot_options = []
for day in avail:
    for slot in day["slots"]:
        label = f"{day['date']} ({day['weekday']}) — {slot['start_time'][11:16]}"
        slot_options.append((label, slot["start_time"]))

if not slot_options:
    st.warning("كل الفترات محجوزة حالياً. تحقق لاحقاً.")
    st.stop()

selected_label, selected_time = st.selectbox(
    "الوقت المتاح",
    options=slot_options,
    format_func=lambda x: x[0],
)

# ====== الخطوة 3: بيانات العميل ======
st.markdown("### 3️⃣ بياناتك")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("الاسم الكامل *", placeholder="مثال: أحمد محمد")
with col2:
    email = st.text_input("البريد الإلكتروني", placeholder="you@example.com")
phone = st.text_input("رقم الهاتف / واتساب", placeholder="+90...")
notes = st.text_area("ملاحظات (اختياري)", placeholder="أي تفاصيل تود إخبارنا بها")

# ====== الخطوة 4: التأكيد ======
st.markdown("---")
if st.button("✅ تأكيد الحجز", type="primary"):
    if not name or len(name) < 2:
        st.error("الرجاء إدخال الاسم.")
        st.stop()
    payload = {
        "service_id": service_id,
        "start_time": selected_time,
        "customer": {
            "name": name,
            "email": email or None,
            "phone": phone or None,
        },
        "notes": notes or None,
    }
    try:
        r = httpx.post(f"{API_URL}/api/book", json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            st.success("🎉 " + data.get("message", "تم الحجز بنجاح!"))
            st.balloons()
            st.markdown(f"""
            ---
            ### 📋 تفاصيل حجزك
            - **الخدمة:** {service_names.get(service_id)}
            - **الوقت:** {data.get('start_time')}
            - **رابط اللقاء:** {data.get('meeting_url') or 'سيُرسل لاحقاً'}

            📞 للاستفسار: {settings.owner_name}
            📧 {settings.owner_email}
            📱 واتساب: {settings.owner_whatsapp}
            """)
        else:
            try:
                err = r.json().get("detail", r.text)
            except Exception:
                err = r.text
            st.error(f"⚠️ تعذّر الحجز: {err}")
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بالخادم: {e}")

st.markdown("---")
st.caption(f"© {settings.owner_name} • Schedule-ZeroBaran • {datetime.now().year}")
