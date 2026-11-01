# ☁️ Schedule-ZeroBaran — دليل النشر الكامل

## خيارات النشر المتاحة

| الخيار | التكلفة | الميزة | متى تستخدمه؟ |
|---|---|---|---|
| **Vercel + Supabase + GitHub Actions** | مجاني 100% | نشر سحابي كامل بدون خادم | الإعداد الأساسي الموصى به |
| **VPS (مثل Hetzner / DigitalOcean)** | ~5$ شهرياً | سيطرة كاملة | عند الحاجة لأداء عالٍ |
| **محلياً على جهازك** | مجاني | للتطوير والاختبار | أثناء التطوير |

---

## 1️⃣ إعداد Supabase (قاعدة البيانات)

### إنشاء المشروع
1. سجّل في <https://supabase.com> (مجاني).
2. New Project ← اختر اسماً، منطقة، و كلمة مرور قوية لـ PostgreSQL.
3. انتظر حتى يكتمل الإعداد (~2 دقيقة).

### الحصول على المفاتيح
1. ادخل Project Settings ← API.
2. انسخ:
   - **Project URL** ← `SUPABASE_URL`
   - **anon public key** ← `SUPABASE_KEY`
   - **service_role key** ← `SUPABASE_SERVICE_KEY` (سري جداً)

### تنفيذ مخطط قاعدة البيانات
1. ادخل SQL Editor ← New query.
2. انسخ محتوى `sql/schema.sql` كاملاً والصقه.
3. اضغط Run. ستنشأ الجداول والسياسات.

### (اختياري) زرع بيانات أولية
```bash
python scripts/seed_data.py
```

---

## 2️⃣ إعداد Google Gemini API (الذكاء الاصطناعي)

1. ادخل <https://aistudio.google.com/app/apikey>.
2. Create API key ← انسخ المفتاح.
3. ضعه في `GEMINI_API_KEY` في `.env`.
4. النموذج الافتراضي: `gemini-1.5-flash` (مجاني وسريع).

### بديل: Groq API
1. ادخل <https://console.groq.com/keys>.
2. Create API Key ← انسخ.
3. ضع:
   ```env
   AI_PROVIDER=groq
   GROQ_API_KEY=your_key
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

---

## 3️⃣ إعداد بوت تليجرام

### إنشاء البوت
1. افتح تليجرام، ابحث عن **@BotFather**.
2. أرسل `/newbot` ← اتبع التعليمات.
3. احفظ **التوكن** في `TELEGRAM_BOT_TOKEN`.

### الحصول على chat_id الخاص بك
1. ابحث عن **@userinfobot** وابدأ معه.
2. انسخ الـ `Id` في `TELEGRAM_OWNER_CHAT_ID`.

### اختبار البوت
```bash
python -c "
from app.telegram_bot import TelegramGateway
from app.config import settings
tg = TelegramGateway()
print(tg.notify_owner('🧪 اختبار اتصال Schedule-ZeroBaran'))
"
```

---

## 4️⃣ النشر على Vercel (موصى به)

### الخطوات
1. ارفع المشروع إلى GitHub (مستودع خاص أو عام).
2. ادخل <https://vercel.com> ← New Project.
3. استورد المستودع.
4. في Environment Variables، أضف جميع متغيرات `.env`.
5. اضغط Deploy.

### بعد النشر
- الـ API سيكون على: `https://your-app.vercel.app`
- توثيق Swagger: `https://your-app.vercel.app/docs`
- **Crons**: سيعمل Vercel Cron تلقائياً حسب `vercel.json`:
  - كل ساعة: استدعاء `/api/reminders/run`
  - يومياً منتصف الليل: استدعاء `/api/cleanup`

> ملاحظة: Vercel يسمح بمجاناً بـ 2 cron jobs للمشاريع المجانية.

---

## 5️⃣ نشر Streamlit Dashboard

Streamlit لا يعمل على Vercel مباشرة. الخيارات:

### أ) Streamlit Community Cloud (مجاني)
1. ادخل <https://share.streamlit.io>.
2. اربط حساب GitHub.
3. اختر المستودع وملف `dashboard/app.py`.
4. أضف Environment Variables.
5. Deploy.

### ب) تشغيل على VPS
```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

ثم استخدم Nginx كـ reverse proxy:

```nginx
server {
    listen 80;
    server_name dashboard.yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 6️⃣ تفعيل GitHub Actions (للتذكيرات المجدولة)

> ملاحظة: إذا نشرت على Vercel، الـ Crons ستعمل تلقائياً. يمكنك استخدام GitHub Actions كبديل أو إضافة.

### إضافة الأسرار
1. على GitHub، ادخل المستودع ← Settings ← Secrets and variables ← Actions.
2. أضف Repository Secret لكل متغير في `.env`:
   - `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`
   - `GEMINI_API_KEY`, `GROQ_API_KEY`, `AI_PROVIDER`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID`
   - `DEFAULT_MEETING_URL`, `TIMEZONE`
   - `SESSION_DURATION_MINUTES`, `AVAILABILITY_WINDOW_DAYS`

### تفعيل السير
- سيعمل `reminders.yml` كل ساعة تلقائياً.
- يمكنك تشغيله يدوياً من تبويب Actions ← Run workflow.

### ملاحظة مهمة عن الجدولة
GitHub Actions قد يتأخر دقائق عن الوقت المحدد في الفترات المزدحمة. للحصول على دقة أعلى، استخدم Vercel Crons أو خادم خاص مع APScheduler.

---

## 7️⃣ النشر على VPS (متقدم)

```bash
# تحديث النظام
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx

# استنساخ المشروع
git clone https://github.com/yourusername/Schedule-ZeroBaran.git
cd Schedule-ZeroBaran

# بيئة افتراضية
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# إعداد .env
cp .env.example .env
nano .env  # املأ القيم

# تشغيل الـ API عبر systemd
sudo tee /etc/systemd/system/zerobaran-api.service > /dev/null <<EOF
[Unit]
Description=Schedule-ZeroBaran API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Schedule-ZeroBaran
EnvironmentFile=/home/ubuntu/Schedule-ZeroBaran/.env
ExecStart=/home/ubuntu/Schedule-ZeroBaran/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now zerobaran-api
```

وكرّر العملية لـ Streamlit والبوت.

---

## ✅ قائمة تحقق النشر

- [ ] Supabase منشأ، schema منفّذ، مفاتيح محفوظة في `.env`.
- [ ] مفتاح Gemini أو Groq فعّال.
- [ ] بوت تليجرام منشأ، chat_id صحيح، اختبار الإرسال ناجح.
- [ ] الـ API يعمل: `curl https://your-app.vercel.app/health` يُرجع `{"status":"ok"}`.
- [ ] زرع بيانات أولية: `python scripts/seed_data.py`.
- [ ] فحص صحة: `python scripts/health_check.py` — كل الفحوصات ✅.
- [ ] Crons مفعّلة (Vercel أو GitHub Actions).
- [ ] Streamlit Dashboard منشور ويمكن الوصول إليه.
- [ ] واجهة حجز العميل متاحة للعملاء.

---

## 🆘 استكشاف الأخطاء

### `❌ إعدادات Supabase غير مكتملة`
- تأكد أن `SUPABASE_URL` و `SUPABASE_KEY` (أو `SUPABASE_SERVICE_KEY`) في `.env`.

### `⚠️ TELEGRAM_BOT_TOKEN غير مضبوط`
- أضف التوكن في `.env` أو في أسرار GitHub/Vercel.

### `تعذّر توليد الرد عبر Gemini`
- تأكد أن `GEMINI_API_KEY` صالح وأن النموذج `gemini-1.5-flash` متاح لحسابك.
- جرّب التبديل إلى Groq بتغيير `AI_PROVIDER=groq`.

### `GitHub Actions لم يعمل في موعده`
- الجدولة قد تتأخر دقائق في الفترات المزدحمة (طبيعي).
- شغّل السير يدوياً للتأكد من عمله.

### `الإتاحة فارغة دائماً`
- تأكد من وجود صفوف في `working_hours` لليوم المطلوب.
- تأكد من أن اليوم ضمن نافذة `AVAILABILITY_WINDOW_DAYS`.

---

© 2026 Baran Avisat — Schedule-ZeroBaran
