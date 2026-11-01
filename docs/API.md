# 📡 Schedule-ZeroBaran — مرجع الـ API الكامل

الـ API يعمل على FastAPI ويوفّر توثيقاً تفاعلياً تلقائياً على `/docs` (Swagger) و `/redoc`.

**Base URL (افتراضي):** `http://localhost:8000`

---

## 📋 الفهرس

- [عام](#عام)
- [الإتاحة (Availability)](#الإتاحة-availability)
- [الحجز (Booking)](#الحجز-booking)
- [المواعيد (Appointments)](#المواعيد-appointments)
- [ساعات العمل (Working Hours)](#ساعات-العمل-working-hours)
- [التذكيرات والتنظيف](#التذكيرات-والتنظيف)

---

## عام

### `GET /`
معلومات عامة عن المنظومة.

**Response:**
```json
{
  "name": "Schedule-ZeroBaran",
  "version": "1.0.0",
  "author": "Baran Avisat",
  "email": "Baranavisat@gmail.com",
  "whatsapp": "00905313263722"
}
```

### `GET /health`
فحص الحيوية.

**Response:**
```json
{"status": "ok", "service": "schedule-zerobaran", "tz": "Europe/Istanbul"}
```

---

## الإتاحة (Availability)

### `GET /api/services`
يُرجع قائمة الخدمات النشطة.

**Response:**
```json
{
  "services": [
    {
      "id": "uuid-...",
      "name": "استشارة عامة",
      "description": "جلسة استشارية مدتها ساعة",
      "duration_minutes": 60,
      "price": 0,
      "is_active": true
    }
  ]
}
```

### `GET /api/availability?days=7`
يُرجع الإتاحة لعدد أيام قادمة.

**Query params:**
- `days` (int, default=7, min=1, max=60)

**Response:**
```json
{
  "availability": [
    {
      "date": "2026-11-01",
      "weekday": "السبت",
      "slots": [
        {
          "start_time": "2026-11-01T09:00:00+03:00",
          "end_time": "2026-11-01T10:00:00+03:00",
          "duration_minutes": 60,
          "is_available": true
        }
      ],
      "slots_count": 8
    }
  ]
}
```

### `GET /api/availability/{target_date}`
يُرجع الفترات المتاحة في تاريخ محدد.

**Path param:** `target_date` بصيغة `YYYY-MM-DD`

**Query params:**
- `service_id` (optional) — لاحتساب مدة الخدمة

---

## الحجز (Booking)

### `POST /api/book`
حجز موعد جديد مع فحص التعارض والتأكيد الفوري.

**Request body:**
```json
{
  "service_id": "uuid-of-service",
  "start_time": "2026-11-05T14:00:00+03:00",
  "customer": {
    "name": "أحمد محمد",
    "email": "ahmed@example.com",
    "phone": "+905551234567",
    "telegram_id": 123456789,
    "notes": "أي تفاصيل إضافية"
  },
  "notes": "ملاحظات الحجز"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "appointment_id": "uuid-...",
  "message": "تم تأكيد حجزك بنجاح! ستصل تذكيرات قبل الموعد.",
  "meeting_url": "https://meet.google.com/...",
  "start_time": "2026-11-05T14:00:00+03:00",
  "end_time": "2026-11-05T15:00:00+03:00"
}
```

**Conflict Response (409):**
```json
{"detail": "⚠️ هذه الفترة محجوزة بالفعل أو متداخلة مع موعد آخر. اختر وقتاً آخر."}
```

**الآثار الجانبية:**
- يُدرج صف في `appointments`.
- يُرسل إشعاراً فورياً للمالك عبر تليجرام.
- يُولّد رسالة تأكيد عبر الذكاء الاصطناعي ويُرسلها للعميل.

---

## المواعيد (Appointments)

### `GET /api/appointments`
قائمة المواعيد خلال فترة.

**Query params:**
- `from_date` (ISO datetime, default=now)
- `to_date` (ISO datetime, default=now+30d)
- `status` (one of: pending, confirmed, completed, cancelled, no_show)

**Response:**
```json
{
  "appointments": [...],
  "count": 5
}
```

### `GET /api/appointments/{appointment_id}`
تفاصيل موعد محدد.

### `PATCH /api/appointments/{appointment_id}`
تحديث حالة موعد.

**Body:**
```json
{
  "status": "confirmed",
  "notes": "تم تأكيد الموعد هاتفياً",
  "meeting_url": "https://meet.google.com/new-link"
}
```

### `POST /api/appointments/{appointment_id}/cancel`
إلغاء موعد (يحدّث الحالة إلى `cancelled`).

---

## ساعات العمل (Working Hours)

### `GET /api/working-hours`
قائمة قواعد ساعات العمل النشطة.

### `POST /api/working-hours`
إضافة/تحديث قواعد ساعات العمل.

**Body:**
```json
[
  {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "is_active": true},
  {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00", "is_active": true}
]
```

> `day_of_week`: 0=الأحد, 1=الإثنين, ..., 6=السبت

### `POST /api/schedule-exceptions?date=2026-12-25&reason=عطلة`
إضافة استثناء (يوم عطلة كامل).

---

## التذكيرات والتنظيف

### `POST /api/reminders/run`
تشغيل دورة تذكيرات يدوياً (مفيد للاختبار أو الـ Cron الخارجي).

**Response:**
```json
{
  "reminders_sent": 3,
  "appointments_completed": 1,
  "run_at": "2026-11-01T13:00:00+03:00"
}
```

### `POST /api/cleanup`
تنظيف المواعيد المنتهية (تحديث حالتها إلى `completed`).

**Response:**
```json
{"completed": 5}
```

---

## أمثلة استخدام

### Python (httpx)

```python
import httpx

BASE = "http://localhost:8000"

# عرض الإتاحة
r = httpx.get(f"{BASE}/api/availability", params={"days": 7})
avail = r.json()["availability"]

# حجز موعد
r = httpx.post(f"{BASE}/api/book", json={
    "service_id": "uuid-here",
    "start_time": avail[0]["slots"][0]["start_time"],
    "customer": {"name": "أحمد", "email": "a@b.com", "phone": "+90..."}
})
print(r.json())
```

### JavaScript (fetch)

```javascript
const res = await fetch('https://your-app.vercel.app/api/book', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    service_id: 'uuid-here',
    start_time: '2026-11-05T14:00:00+03:00',
    customer: { name: 'Ahmed', email: 'a@b.com' }
  })
});
const data = await res.json();
console.log(data);
```

### cURL

```bash
# عرض الخدمات
curl https://your-app.vercel.app/api/services

# حجز موعد
curl -X POST https://your-app.vercel.app/api/book \
  -H "Content-Type: application/json" \
  -d '{"service_id":"...","start_time":"2026-11-05T14:00:00+03:00","customer":{"name":"Ahmed"}}'
```

---

## رموز الأخطاء

| الكود | المعنى |
|---|---|
| 200 | نجاح |
| 400 | طلب غير صالح (تاريخ خاطئ مثلاً) |
| 404 | غير موجود |
| 409 | تعارض (الموعد محجوز) |
| 500 | خطأ داخلي في الخادم |

---

© 2026 Baran Avisat — Schedule-ZeroBaran
