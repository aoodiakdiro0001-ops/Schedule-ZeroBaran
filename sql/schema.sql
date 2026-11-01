-- ============================================================
-- Schedule-ZeroBaran — Supabase / PostgreSQL Schema
-- المؤلف: Baran Avisat (Baranavisat@gmail.com)
-- ============================================================
-- نفّذ هذا الملف في Supabase SQL Editor لإنشاء الجداول.
-- ============================================================

-- تفعيل الإضافات اللازمة
create extension if not exists "pgcrypto";

-- ====== جدول ساعات العمل (Working Hours) ======
create table if not exists working_hours (
    id              uuid primary key default gen_random_uuid(),
    day_of_week     smallint not null check (day_of_week between 0 and 6),
    -- 0=الأحد, 1=الإثنين, ..., 6=السبت
    start_time      time not null,
    end_time        time not null,
    is_active       boolean default true,
    created_at      timestamptz default now(),
    unique (day_of_week, start_time, end_time)
);

-- ====== جدول الاستثناءات (عطل/إجازات) ======
create table if not exists schedule_exceptions (
    id              uuid primary key default gen_random_uuid(),
    exception_date  date not null unique,
    reason          text,
    created_at      timestamptz default now()
);

-- ====== جدول الخدمات (Services) ======
create table if not exists services (
    id              uuid primary key default gen_random_uuid(),
    name            text not null,
    description     text,
    duration_minutes integer default 60,
    price           numeric(10,2) default 0,
    is_active       boolean default true,
    created_at      timestamptz default now()
);

-- ====== جدول العملاء (Customers) ======
create table if not exists customers (
    id              uuid primary key default gen_random_uuid(),
    name            text not null,
    email           text,
    phone           text,
    telegram_id     bigint,
    notes           text,
    created_at      timestamptz default now(),
    unique (telegram_id)
);

-- ====== جدول المواعيد (Appointments) — الجدول المحوري ======
create table if not exists appointments (
    id              uuid primary key default gen_random_uuid(),
    customer_id     uuid references customers(id) on delete set null,
    service_id      uuid references services(id) on delete set null,
    customer_name   text not null,
    customer_email  text,
    customer_phone  text,
    customer_telegram_id bigint,
    service_name    text,
    start_time      timestamptz not null,
    end_time        timestamptz not null,
    status          text not null default 'pending'
                    check (status in ('pending','confirmed','cancelled','completed','no_show')),
    meeting_url     text,
    notes           text,
    reminder_sent   boolean default false,
    confirmation_message text,
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

-- فهرس لفحص التعارض بسرعة
create index if not exists idx_appointments_start_end
    on appointments (start_time, end_time);
create index if not exists idx_appointments_status
    on appointments (status);
create index if not exists idx_appointments_reminder
    on appointments (reminder_sent, start_time)
    where status in ('confirmed','pending');

-- ====== جدول سجل الإشعارات (Notifications Log) ======
create table if not exists notifications_log (
    id              uuid primary key default gen_random_uuid(),
    appointment_id  uuid references appointments(id) on delete cascade,
    channel          text not null check (channel in ('telegram','email','sms','webhook')),
    recipient       text not null,
    payload         jsonb,
    status          text default 'sent',
    sent_at         timestamptz default now()
);

-- ====== إدراج ساعات عمل افتراضية (الإثنين-الجمعة 9ص-5م) ======
insert into working_hours (day_of_week, start_time, end_time, is_active)
values
    (1, '09:00', '17:00', true),  -- الإثنين
    (2, '09:00', '17:00', true),  -- الثلاثاء
    (3, '09:00', '17:00', true),  -- الأربعاء
    (4, '09:00', '17:00', true),  -- الخميس
    (5, '09:00', '17:00', true)   -- الجمعة
on conflict (day_of_week, start_time, end_time) do nothing;

-- ====== إدراج خدمة افتراضية ======
insert into services (name, description, duration_minutes, price)
values
    ('استشارة عامة', 'جلسة استشارية مدتها ساعة كاملة', 60, 0),
    ('جلسة متابعة', 'جلسة متابعة قصيرة 30 دقيقة', 30, 0),
    ('اجتماع عمل', 'اجتماع عمل 45 دقيقة', 45, 0)
on conflict do nothing;

-- ====== Row Level Security (الأمان) ======
-- تفعيل RLS
alter table working_hours enable row level security;
alter table schedule_exceptions enable row level security;
alter table services enable row level security;
alter table customers enable row level security;
alter table appointments enable row level security;
alter table notifications_log enable row level security;

-- سياسات السماح بالقراءة العامة لساعات العمل والخدمات (للعملاء)
create policy "public read working hours" on working_hours for select using (true);
create policy "public read services" on services for select using (is_active = true);

-- باقي الجداول يُدار الوصول إليها عبر مفتاح الخدمة (Service Role)
-- يمكن إضافة سياسات أكثر تحديداً حسب الحاجة

-- ============================================================
-- نهاية المخطط — Schedule-ZeroBaran © Baran Avisat
-- ============================================================
