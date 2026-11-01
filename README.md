<div align="center">

# 🗓️ Schedule-ZeroBaran

### المنظومة الذاتية الذكية لحجز المواعيد، الجدولة، وإدارة الأجندة

**نظام ذكي متكامل ومستقل لإدارة المواعيد، حجز الاستشارات أو الجلسات، مزامنة التقويم، وإرسال التذكيرات الآلية — بُني بالكامل بموارد مجانية 100%.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Free Tier](https://img.shields.io/badge/Cost-100%25%20Free-success.svg)](#)

</div>

---

## 🌟 ما هو Schedule-ZeroBaran؟

هو **نظام ذكي متكامل ومستقل** لإدارة المواعيد، حجز الاستشارات أو الجلسات، مزامنة التقويم، وإرسال التذكيرات الآلية. يقوم بـ:

- 📅 عرض أوقات فراغك المتاحة للعملاء
- 📥 استقبال طلبات الحجز
- ⚖️ التحقق من عدم تعارض المواعيد
- 💾 حجز الموعد في قاعدة البيانات
- 🤖 توليد روابط اجتماعات افتراضية أو إرسال تذكيرات ذكية للعملاء قبل الموعد

**كل ذلك دون دفع دولار واحد لأي منصة جدولة مدفوعة، وبموارد مجانية بالكامل.**

---

## 💡 لماذا تتمنى كل شركة وكل فرد الحصول عليه؟

| الميزة | الوصف |
|---|---|
| 💰 **توفير مال فلكي** | اشتراكات أدوات الجدولة والمواعيد تكلف مبالغ طائلة سنوياً؛ هذا النظام يؤدي نفس الغرض بتكلفة صفر. |
| ⚡ **القضاء على الفوضى (Zero Scheduling Friction)** | بدلاً من رسائل الأخذ والعطاء الطويلة، يختار العميل وقتاً متاحاً بضغطة زر ويتم تثبيته فوراً. |
| 🔒 **السيادة والخصوصية التامة** | جدولك ومواعيد عملائك تبقى مخزنة في بيئة سرية خاصة بك دون وسطاء. |

---

## 🛠️ الموارد المجانية البحتة المستخدمة (The Free Tech Stack)

| المكون | الخدمة / التقنية | الدور |
|---|---|---|
| 🔄 محرك التشغيل والمتابعة المجدولة (Cron) | **GitHub Actions** | خادم مجاني لتنفيذ التذكيرات الآلية وتحديث حالة المواعيد المنتهية دورياً. |
| ⚙️ محرك المعالجة والمنطق الزمني | **Python + FastAPI / Vercel Serverless** | إدارة الفترات المتاحة، حساب التداخلات، ومعالجة طلبات الحجز. |
| 💾 قاعدة البيانات وسجل الحجوزات | **Supabase (PostgreSQL Free Tier)** | تخزين المواعيد، الجداول الزمنية، بيانات العملاء. |
| 🧠 محرك الذكاء الاصطناعي | **Google Gemini API / Groq API (Free Tiers)** | صياغة رسائل الترحيب، تكييف المواعيد، والإجابة على استفسارات العملاء. |
| 📱 قناة الاستقبال والتنبيهات | **Telegram Bot API / Streamlit Dashboard** | واجهة تفاعلية للعملاء لحجز المواعيد واستلام إشعارات فورية. |

---

## 📐 البنية البرمجية (Software Architecture)

يتكون النظام من **4 طبقات برمجية متناسقة** تعمل كمنظومة سكرتير رقمي ذكي:

```
[دخول العميل لرابط الحجز واختيار الوقت المناسب (عبر واجهة أو تليجرام)]
                                  │
                                  ▼
[Supabase (فحص الجدول الزمني والتأكد من خلو الموعد وتجنب التعارض)]
                                  │
                                  ▼
[Python / Vercel Serverless (تثبيت الحجز وإرسال تفاصيل الجلسة)]
                                  │
                                  ▼
[Google Gemini API (صياغة التأكيد) ──► إشعار فوري للمالك وتذكير للعميل]
```

### تفصيل الطبقات

#### 1️⃣ طبقة عرض الأوقات وإدارة الجدول (Availability Layer)
- **التقنية:** قاعدة بيانات Supabase مرتبطة بواجهة Streamlit أو بوت تليجرام.
- **الآلية:** يستعرض النظام الأوقات المتاحة بناءً على أيام عملك وساعات فراغك، مع إخفاء المواعيد المحجوزة مسبقاً تلقائياً.

#### 2️⃣ طبقة الحجز ومنع التعارض (Booking & Conflict Prevention)
- **التقنية:** سكريبت بايثون / Serverless Function.
- **الآلية:** عندما يختار العميل وقتاً، يفحص النظام قاعدة البيانات فوراً للتأكد من عدم حجز نفس اللحظة من قِبل عميل آخر، ثم يُثبت الحجز بدقة متناهية.

#### 3️⃣ طبقة التذكير الذكي (Automated Reminder Core)
- **التقنية:** خادم GitHub Actions.
- **الآلية:** يفحص جدول المواعيد بانتظام، ويرسل تذكيرات آلية للعميل قبل موعده بساعة أو يوم لضمان عدم تغيبه.

#### 4️⃣ طبقة التوصيل والتنبيه (Delivery & UI)
- **التقنية:** Telegram Bot + Streamlit Dashboard.
- **الآلية:** يرسل لك تنبيهاً فورياً على هاتفك:
  ```
  📅 موعد جديد مؤكد: جلسة استشارة مع العميل [اسم العميل]
  ⏰ الوقت: غداً الساعة 4:00 عصراً.
  🔗 رابط اللقاء / التفاصيل: (مدرجة ومجهزة تلقائياً).
  ```

---

## ⚙️ طريقة العمل خطوة بخطوة (End-to-End Workflow)

1. **الحدث:** يرغب عميل في حجز موعد معك، فيدخل على رابط النظام أو يفتح بوت تليجرام الخاص بك.
2. **اختيار الوقت:** يعرض النظام الأوقات الشاغرة الحقيقية في جدولك دون أي تداخل.
3. **التثبيت الآلي:** يختار العميل الساعة المناسبة، فيسجل النظام الحجز فوراً في Supabase ويحجب هذا الوقت نهائياً.
4. **النتيجة الفورية:** يأتيك إشعار فوري على هاتفك بتفاصيل الحجز، ويصل العميل رسالة تأكيد مخصصة، وكل ذلك يتم بلا توقف ودون دفع سنت واحد.

---

## 📁 بنية المشروع (Project Structure)

```
Schedule-ZeroBaran/
├── app/                          # التطبيق الأساسي (FastAPI + المنطق)
│   ├── __init__.py
│   ├── main.py                   # تطبيق FastAPI الرئيسي
│   ├── config.py                 # الإعدادات المركزية
│   ├── database.py               # طبقة Supabase وقاعدة البيانات
│   ├── models.py                 # نماذج Pydantic
│   ├── scheduler.py              # محرك الجدولة وحساب الإتاحة
│   ├── ai_brain.py               # طبقة الذكاء الاصطناعي (Gemini/Groq)
│   ├── telegram_bot.py           # بوت تليجرام وقناة التنبيهات
│   └── reminders.py              # محرك التذكيرات الذكي
├── dashboard/                    # لوحة تحكم المالك (Streamlit)
│   └── app.py
├── booking_ui/                   # واجهة حجز العميل (Streamlit)
│   └── app.py
├── api/                          # نقطة دخول Vercel Serverless
│   └── index.py
├── sql/                          # مخطط قاعدة البيانات
│   └── schema.sql
├── scripts/                      # سكربتات التشغيل
│   ├── send_reminders.py         # إرسال التذكيرات (يُشغّل عبر GitHub Actions)
│   ├── cleanup_appointments.py   # تنظيف المواعيد المنتهية
│   ├── seed_data.py              # زرع بيانات أولية
│   └── health_check.py           # فحص سلامة المكوّنات
├── .github/workflows/            # سير عمل GitHub Actions
│   ├── reminders.yml             # دورة التذكيرات كل ساعة
│   └── cleanup.yml               # تنظيف يومي
├── docs/                         # التوثيق
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── API.md
├── requirements.txt              # متطلبات Python
├── .env.example                  # نموذج متغيرات البيئة
├── vercel.json                   # إعدادات النشر على Vercel
├── LICENSE                       # ترخيص MIT مع حقوق المؤلف
├── AUTHOR_INFO.md                # معلومات المؤلف والدعم
└── README.md                     # هذا الملف
```

---

## 🚀 دليل البدء السريع (Quick Start)

### المتطلبات المسبقة

- Python 3.11 أو أحدث
- حساب مجاني على [Supabase](https://supabase.com)
- مفتاح API مجاني من [Google Gemini](https://aistudio.google.com/app/apikey) أو [Groq](https://console.groq.com/keys)
- (اختياري) بوت تليجرام من [@BotFather](https://t.me/BotFather)
- (اختياري) حساب [GitHub](https://github.com) لتفعيل التذكيرات المجدولة

### الخطوة 1: نسخ المشروع

```bash
unzip Schedule-ZeroBaran.zip
cd Schedule-ZeroBaran
```

### الخطوة 2: إعداد البيئة الافتراضية

```bash
python -m venv .venv
source .venv/bin/activate  # على Linux/macOS
# أو على Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### الخطوة 3: إعداد المتغيرات البيئية

```bash
cp .env.example .env
```

افتح ملف `.env` واملأ القيم بمفاتيحك الحقيقية:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOi...
SUPABASE_SERVICE_KEY=eyJhbGciOi...

GEMINI_API_KEY=AIza...
AI_PROVIDER=gemini

TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_OWNER_CHAT_ID=123456789
DEFAULT_MEETING_URL=https://meet.google.com/your-room

TIMEZONE=Europe/Istanbul
SESSION_DURATION_MINUTES=60
AVAILABILITY_WINDOW_DAYS=14

OWNER_NAME=Baran Avisat
OWNER_EMAIL=Baranavisat@gmail.com
OWNER_WHATSAPP=00905313263722
```

### الخطوة 4: إعداد قاعدة بيانات Supabase

1. ادخل إلى لوحة Supabase ← SQL Editor.
2. انسخ محتوى `sql/schema.sql` والصقه، ثم نفّذه (Run).
3. (اختياري) زرع بيانات أولية:
   ```bash
   python scripts/seed_data.py
   ```

### الخطوة 5: تشغيل المحرك الرئيسي

```bash
python -m app.main
# أو
uvicorn app.main:app --reload --port 8000
```

سيكون الـ API متاحاً على: <http://localhost:8000>

توثيق الـ API التفاعلي: <http://localhost:8000/docs>

### الخطوة 6: تشغيل لوحة التحكم (للمالك)

```bash
streamlit run dashboard/app.py
```

### الخطوة 7: تشغيل واجهة الحجز (للعميل)

```bash
streamlit run booking_ui/app.py
```

### الخطوة 8: تشغيل بوت تليجرام (اختياري)

```bash
python -m app.telegram_bot
```

ثم على تليجرام، ابدأ مع البوت: `/start` لعرض الخدمات.

---

## ☁️ خيارات النشر (Deployment)

### أ) النشر على Vercel (مجاني)

1. ارفع المشروع إلى مستودع GitHub.
2. ادخل [vercel.com](https://vercel.com) ← New Project ← استورد المستودع.
3. أضف متغيرات البيئة من `.env` في إعدادات Vercel.
4. انشر. الـ API سيعمل على `https://your-app.vercel.app`.
5. سيتولّى Vercel تشغيل الـ Crons (المعرّفة في `vercel.json`) مجاناً.

### ب) النشر على خادم خاص (VPS)

```bash
# تثبيت
pip install -r requirements.txt

# تشغيل الـ API عبر Gunicorn + Uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

# تشغيل لوحة التحكم
streamlit run dashboard/app.py --server.port 8501

# تشغيل البوت (في عملية منفصلة)
python -m app.telegram_bot
```

### ج) تفعيل GitHub Actions للتذكيرات

1. ارفع المشروع إلى GitHub.
2. في إعدادات المستودع: Settings ← Secrets and variables ← Actions.
3. أضف كل متغيرات `.env` كـ Repository Secrets.
4. سيعمل سير العمل `reminders.yml` تلقائياً كل ساعة.

---

## 📡 وثائق الـ API

| الطريقة | المسار | الوصف |
|---|---|---|
| GET | `/` | معلومات المنظومة |
| GET | `/health` | فحص الحيوية |
| GET | `/api/services` | قائمة الخدمات |
| GET | `/api/availability?days=7` | الإتاحة لعدد أيام |
| GET | `/api/availability/{date}` | الإتاحة ليوم محدد |
| POST | `/api/book` | حجز موعد جديد |
| GET | `/api/appointments` | قائمة المواعيد |
| GET | `/api/appointments/{id}` | موعد محدد |
| PATCH | `/api/appointments/{id}` | تحديث حالة موعد |
| POST | `/api/appointments/{id}/cancel` | إلغاء موعد |
| GET | `/api/working-hours` | ساعات العمل |
| POST | `/api/working-hours` | ضبط ساعات العمل |
| POST | `/api/schedule-exceptions` | إضافة استثناء (إجازة) |
| POST | `/api/reminders/run` | تشغيل التذكيرات يدوياً |
| POST | `/api/cleanup` | تنظيف المواعيد المنتهية |

### مثال: حجز موعد عبر cURL

```bash
curl -X POST http://localhost:8000/api/book \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "uuid-of-service",
    "start_time": "2026-11-05T14:00:00+03:00",
    "customer": {
      "name": "أحمد محمد",
      "email": "ahmed@example.com",
      "phone": "+905551234567"
    },
    "notes": "أفضل وقت للاتصال بعد الظهر"
  }'
```

راجع `docs/API.md` للتفاصيل الكاملة.

---

## 🧪 الاختبار والفحص

```bash
# فحص سلامة كل المكوّنات
python scripts/health_check.py

# تشغيل دورة تذكيرات يدوية
python scripts/send_reminders.py

# تنظيف المواعيد المنتهية
python scripts/cleanup_appointments.py
```

---

## 🔒 الأمان والخصوصية

- جميع البيانات مخزّنة في قاعدة بيانات Supabase الخاصة بك.
- صفوف الجداول محمية بـ Row Level Security (RLS).
- مفاتيح الـ API تُحفظ في متغيرات البيئة فقط ولا تُكتب في الكود.
- لا تُشارَك بياناتك مع أي طرف ثالث.
- **أنت المالك الوحيد لجدولك وسجلاتك.**

---

## 📞 الدعم والتواصل

| القناة | البيانات |
|---|---|
| 👤 المؤلف | Baran Avisat |
| 📧 البريد الإلكتروني | Baranavisat@gmail.com |
| 📱 واتساب | +90 531 326 3722 |

للاستفسارات الفنية أو طلبات التطوير المخصص، تواصل عبر القنوات أعلاه.

---

## 📜 الترخيص وحقوق الملكية

هذا المشروع مرخّص برخصة **MIT** — انظر [LICENSE](LICENSE).

```
Copyright (c) 2026 Baran Avisat (Baranavisat@gmail.com)
```

- ✅ يُسمح بالاستخدام الشخصي والتجاري.
- ✅ يُسمح بالتعديل والتطوير.
- ❌ **يُمنع** حذف اسم المؤلف وحقوق الملكية من الكود.

هذا المشروع هو **الحادي والعشرون** في سلسلة ابتكارات المؤلف البرمجية،
وقد تم حفظه في سجلات قاعدة بيانات الابتكار البرمجي لضمان عدم تكراره.

---

<div align="center">

**© 2026 Baran Avisat — Schedule-ZeroBaran**

المنظومة الذاتية الذكية لحجز المواعيد، الجدولة، وإدارة الأجندة

📧 Baranavisat@gmail.com · 📱 +90 531 326 3722

</div>

---

## 🧾 بيانات المالك وحقوق الملكية (Owner & Copyright)

| الحقل | القيمة |
|---|---|
| **المؤلف / Owner** | **Baran Avisat** |
| **البريد / Email** | [baranavisat@gmail.com](mailto:baranavisat@gmail.com) |
| **واتساب / WhatsApp** | +90 531 326 37 22 |
| **الحساب البنكي / IBAN** | `TR10 0001 0090 1008 4013 0050 01` |
| **GitHub** | [github.com/aoodiakdiro0001-ops](https://github.com/aoodiakdiro0001-ops) |
| **المتجر / Store** | [baranavi.gumroad.com](https://baranavi.gumroad.com/) |
| **الترخيص / License** | MIT License (with attribution) |

**© 2026 Baran Avisat — جميع الحقوق محفوظة / All Rights Reserved.**
