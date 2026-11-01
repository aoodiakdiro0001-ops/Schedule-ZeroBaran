"""
Schedule-ZeroBaran — طبقة التوصيل والتنبيه عبر Telegram Bot
المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from .config import settings
from .database import NotificationsLogRepo

logger = logging.getLogger(__name__)


class TelegramGateway:
    """قناة الإرسال والاستقبال عبر Telegram Bot API."""

    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self) -> None:
        self.token = settings.telegram_bot_token
        self.owner_chat_id = settings.telegram_owner_chat_id

    def _url(self, method: str) -> str:
        return self.BASE_URL.format(token=self.token, method=method)

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[dict] = None,
    ) -> dict:
        """يرسل رسالة إلى chat_id. يطلق استثناء عند فشل الاتصال."""
        if not self.token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN غير مضبوط — تخطّي الإرسال.")
            return {"ok": False, "skipped": True}

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(self._url("sendMessage"), json=payload)
                data = resp.json()
            if not data.get("ok"):
                logger.error("❌ فشل إرسال تليجرام: %s", data)
            return data
        except Exception as e:
            logger.error("❌ استثناء أثناء الإرسال لتليجرام: %s", e)
            return {"ok": False, "error": str(e)}

    def notify_owner(self, text: str) -> dict:
        """إشعار المالك فوراً بحجز جديد."""
        if not self.owner_chat_id:
            logger.warning("⚠️ TELEGRAM_OWNER_CHAT_ID غير مضبوط.")
            return {"ok": False}
        return self.send_message(self.owner_chat_id, text)

    def notify_customer(self, telegram_id: Optional[int], text: str, appointment_id: Optional[str] = None) -> dict:
        """إرسال رسالة للعميل عبر تليجرام إن أمكن."""
        if not telegram_id:
            # تسجيل أن الإرسال لم يكن ممكناً
            if appointment_id:
                NotificationsLogRepo.add({
                    "appointment_id": appointment_id,
                    "channel": "telegram",
                    "recipient": "n/a",
                    "payload": {"text": text, "reason": "no_telegram_id"},
                    "status": "skipped",
                })
            return {"ok": False, "reason": "no_telegram_id"}
        result = self.send_message(str(telegram_id), text)
        if appointment_id:
            NotificationsLogRepo.add({
                "appointment_id": appointment_id,
                "channel": "telegram",
                "recipient": str(telegram_id),
                "payload": {"text": text},
                "status": "sent" if result.get("ok") else "failed",
            })
        return result


# ===== بوت الاستقبال التفاعلي (Inline Booking Bot) =====
def build_inline_keyboard(services: list[dict]) -> dict:
    """يبني لوحة أزرار inline لاختيار الخدمة."""
    keyboard = [[{"text": s["name"], "callback_data": f"svc:{s['id']}"}] for s in services]
    return {"inline_keyboard": keyboard}


def run_bot_polling() -> None:
    """
    يشغّل بوت تليجرام في وضع polling (محلياً أو على خادم).
    للنشر في Vercel استخدم webhooks بدلاً من polling.
    """
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )

    from .database import ServicesRepo
    from .scheduler import get_availability_for_days
    from .ai_brain import craft_welcome_message

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        services = ServicesRepo.list_active()
        names = [s["name"] for s in services]
        welcome = craft_welcome_message(
            update.effective_user.first_name or "عزيزي العميل",
            names or ["استشارة عامة"],
        )
        keyboard = [
            [InlineKeyboardButton(s["name"], callback_data=f"svc:{s['id']}")]
            for s in services
        ]
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(welcome, reply_markup=reply_markup)

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 <b>Schedule-ZeroBaran Bot</b>\n\n"
            "/start — بدء الحجز\n"
            "/slots — عرض الأوقات المتاحة\n"
            "/contact — معلومات التواصل\n"
            "/about — عن المنظومة",
            parse_mode="HTML",
        )

    async def slots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        days = get_availability_for_days(7)
        if not days:
            await update.message.reply_text("لا توجد فترات متاحة خلال الأسبوع القادم.")
            return
        lines = ["📅 <b>الفترات المتاحة (7 أيام):</b>\n"]
        for day in days:
            lines.append(f"🔸 <b>{day['date']} ({day['weekday']}):</b> {day['slots_count']} فترة متاحة")
            for slot in day["slots"][:3]:
                lines.append(f"   • {slot['start_time'][11:16]} — {slot['end_time'][11:16]}")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")

    async def contact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"📞 <b>معلومات التواصل</b>\n\n"
            f"👤 {settings.owner_name}\n"
            f"📧 {settings.owner_email}\n"
            f"📱 واتساب: {settings.owner_whatsapp}\n",
            parse_mode="HTML",
        )

    async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚀 <b>Schedule-ZeroBaran</b>\n"
            "منظومة ذاتية ذكية لحجز المواعيد، الجدولة، وإدارة الأجندة.\n\n"
            f"© {settings.owner_name}",
            parse_mode="HTML",
        )

    async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        data = q.data or ""
        if data.startswith("svc:"):
            service_id = data[4:]
            days = get_availability_for_days(5)
            if not days:
                await q.message.reply_text("لا توجد فترات متاحة حالياً.")
                return
            lines = ["اختر فترة من القائمة أدناه (أرسل الأمر بهذا الشكل):", "/book SERVICE_ID YYYY-MM-DDTHH:MM"]
            await q.message.reply_text("\n".join(lines))
            for day in days:
                lines = [f"📅 {day['date']} ({day['weekday']}):"]
                for slot in day["slots"][:5]:
                    lines.append(f"  • /book {service_id} {slot['start_time']}")
                await q.message.reply_text("\n".join(lines))

    async def book_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("الاستخدام: /book SERVICE_ID YYYY-MM-DDTHH:MM")
            return
        from datetime import datetime
        from .scheduler import create_appointment, format_appointment_for_owner
        from .database import ServicesRepo
        service_id = args[0]
        try:
            start_time = datetime.fromisoformat(args[1])
        except ValueError:
            await update.message.reply_text("صيغة الوقت غير صحيحة. مثال: 2026-01-15T14:00")
            return
        service = ServicesRepo.get(service_id)
        try:
            appt = create_appointment(
                start_time=start_time,
                customer={
                    "name": update.effective_user.full_name,
                    "telegram_id": update.effective_user.id,
                },
                service_id=service_id,
            )
            tg = TelegramGateway()
            tg.notify_owner(format_appointment_for_owner(appt))
            await update.message.reply_text(
                f"✅ تم حجز موعدك!\nالخدمة: {service['name'] if service else 'استشارة'}\n"
                f"الوقت: {appt['start_time']}\nالرابط: {appt.get('meeting_url','—')}"
            )
        except ValueError as e:
            await update.message.reply_text(str(e))

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("slots", slots_cmd))
    app.add_handler(CommandHandler("contact", contact_cmd))
    app.add_handler(CommandHandler("about", about_cmd))
    app.add_handler(CommandHandler("book", book_cmd))
    app.add_handler(CallbackQueryHandler(on_callback))

    logger.info("🚀 تشغيل بوت تليجرام في وضع polling...")
    app.run_polling(stop_signals=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot_polling()
