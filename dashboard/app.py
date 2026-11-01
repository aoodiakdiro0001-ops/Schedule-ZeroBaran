"""
Schedule-ZeroBaran — لوحة تحكم المالك (Streamlit Dashboard)
يعرض المواعيد القادمة، الإحصائيات، ويسمح بالإدارة.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

# ضبط المسار للسماح باستيراد حزمة app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings  # noqa: E402
from app.database import (  # noqa: E402
    AppointmentsRepo,
    ServicesRepo,
    WorkingHoursRepo,
    ScheduleExceptionsRepo,
)
from app.scheduler import _parse_dt  # noqa: E402

st.set_page_config(
    page_title="Schedule-ZeroBaran — لوحة التحكم",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تنسيقات RTL
st.markdown("""
<style>
    [data-testid="stSidebar"] { direction: rtl; }
    .main .block-container { direction: rtl; padding-top: 1.5rem; }
    h1, h2, h3 { text-align: right !important; }
    .stMetric { direction: rtl; }
</style>
""", unsafe_allow_html=True)


# ====== العنوان ======
st.title("📅 Schedule-ZeroBaran — لوحة التحكم")
st.caption(f"المنظومة الذاتية الذكية لحجز المواعيد • © {settings.owner_name}")

# ====== الشريط الجانبي ======
st.sidebar.markdown(f"""
### 👤 معلومات المالك
**الاسم:** {settings.owner_name}

**البريد:** {settings.owner_email}

**واتساب:** {settings.owner_whatsapp}

**المنطقة الزمنية:** {settings.timezone}
""")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "القائمة",
    ["نظرة عامة", "المواعيد القادمة", "كل المواعيد", "الإتاحة الحالية", "الإعدادات"],
)


def _fmt_dt(value: str) -> str:
    tz = ZoneInfo(settings.timezone)
    return _parse_dt(value).astimezone(tz).strftime("%Y-%m-%d %H:%M")


# ====== نظرة عامة ======
if menu == "نظرة عامة":
    st.header("📊 نظرة عامة")
    now = datetime.now(ZoneInfo(settings.timezone))
    in_week = (now + timedelta(days=7)).isoformat()
    upcoming = AppointmentsRepo.list_between(now.isoformat(), in_week, statuses=["confirmed", "pending"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📅 مواعيد هذا الأسبوع", len(upcoming))
    confirmed = sum(1 for a in upcoming if a["status"] == "confirmed")
    col2.metric("✅ مؤكدة", confirmed)
    pending = sum(1 for a in upcoming if a["status"] == "pending")
    col3.metric("⏳ قيد الانتظار", pending)
    col4.metric("💼 عدد الخدمات", len(ServicesRepo.list_active()))

    st.markdown("---")
    st.subheader("📌 المواعيد القادمة")
    if not upcoming:
        st.info("لا توجد مواعيد قادمة خلال أسبوع.")
    else:
        for appt in upcoming[:10]:
            with st.expander(f"🔹 {appt.get('customer_name')} — {_fmt_dt(appt['start_time'])}"):
                st.write(f"**الخدمة:** {appt.get('service_name') or '—'}")
                st.write(f"**الحالة:** {appt['status']}")
                st.write(f"**البريد:** {appt.get('customer_email') or '—'}")
                st.write(f"**الهاتف:** {appt.get('customer_phone') or '—'}")
                st.write(f"**رابط اللقاء:** {appt.get('meeting_url') or '—'}")
                if appt.get("notes"):
                    st.write(f"**ملاحظات:** {appt['notes']}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ تأكيد", key=f"confirm_{appt['id']}"):
                    AppointmentsRepo.update(appt["id"], {"status": "confirmed"})
                    st.success("تم التأكيد.")
                    st.rerun()
                if col_b.button("❌ إلغاء", key=f"cancel_{appt['id']}"):
                    AppointmentsRepo.update(appt["id"], {"status": "cancelled"})
                    st.warning("تم الإلغاء.")
                    st.rerun()


# ====== المواعيد القادمة ======
elif menu == "المواعيد القادمة":
    st.header("📌 المواعيد القادمة (30 يوماً)")
    now = datetime.now(ZoneInfo(settings.timezone))
    future = (now + timedelta(days=30)).isoformat()
    items = AppointmentsRepo.list_between(now.isoformat(), future, statuses=["confirmed", "pending"])
    if not items:
        st.info("لا توجد مواعيد.")
    else:
        rows = []
        for a in items:
            rows.append({
                "العميل": a.get("customer_name"),
                "الخدمة": a.get("service_name"),
                "البداية": _fmt_dt(a["start_time"]),
                "النهاية": _fmt_dt(a["end_time"]),
                "الحالة": a["status"],
                "الهاتف": a.get("customer_phone") or "",
                "رابط اللقاء": a.get("meeting_url") or "",
            })
        st.dataframe(rows, use_container_width=True)


# ====== كل المواعيد ======
elif menu == "كل المواعيد":
    st.header("🗂️ كل المواعيد")
    status_filter = st.selectbox(
        "الحالة",
        ["all", "pending", "confirmed", "completed", "cancelled", "no_show"],
    )
    statuses = None if status_filter == "all" else [status_filter]
    now = datetime.now(ZoneInfo(settings.timezone))
    start = (now - timedelta(days=90)).isoformat()
    end = (now + timedelta(days=90)).isoformat()
    items = AppointmentsRepo.list_between(start, end, statuses=statuses)
    st.write(f"**عدد النتائج:** {len(items)}")
    if items:
        rows = [{
            "العميل": a.get("customer_name"),
            "الخدمة": a.get("service_name"),
            "البداية": _fmt_dt(a["start_time"]),
            "الحالة": a["status"],
            "تذكير؟": "✅" if a.get("reminder_sent") else "⏳",
        } for a in items]
        st.dataframe(rows, use_container_width=True)


# ====== الإتاحة الحالية ======
elif menu == "الإتاحة الحالية":
    st.header("🗓️ الإتاحة الحالية")
    from app.scheduler import get_availability_for_days
    days = st.slider("عدد الأيام القادمة", 1, 30, 7)
    avail = get_availability_for_days(days)
    if not avail:
        st.warning("لا توجد فترات متاحة.")
    else:
        for day in avail:
            with st.expander(f"📅 {day['date']} ({day['weekday']}) — {day['slots_count']} فترة"):
                for slot in day["slots"]:
                    st.write(f"• {slot['start_time'][11:16]} — {slot['end_time'][11:16]}")


# ====== الإعدادات ======
elif menu == "الإعدادات":
    st.header("⚙️ الإعدادات")
    st.subheader("ساعات العمل الحالية")
    wh = WorkingHoursRepo.list_active()
    days_map = {0: "الأحد", 1: "الإثنين", 2: "الثلاثاء", 3: "الأربعاء", 4: "الخميس", 5: "الجمعة", 6: "السبت"}
    for w in wh:
        st.write(f"• {days_map.get(w['day_of_week'], '?')}: {w['start_time']} — {w['end_time']}")

    st.subheader("إضافة استثناء (إجازة)")
    with st.form("exception_form"):
        ex_date = st.date_input("التاريخ")
        ex_reason = st.text_input("السبب (اختياري)")
        if st.form_submit_button("إضافة"):
            ScheduleExceptionsRepo.add(ex_date.isoformat(), ex_reason)
            st.success(f"تمت إضافة استثناء في {ex_date}")
            st.rerun()

    st.subheader("الخدمات")
    for s in ServicesRepo.list_active():
        st.write(f"• **{s['name']}** — {s.get('duration_minutes',60)} دقيقة — {s.get('price',0)}")
