"""
Schedule-ZeroBaran — طبقة الذكاء الاصطناعي (AI Scheduler Brain)
تدعم Google Gemini و Groq (مجاناً) لتوليد رسائل التأكيد، الترحيب،
والإجابة على استفسارات العملاء حول الخدمات والمواعيد.

المؤلف: Baran Avisat (Baranavisat@gmail.com)
"""
from __future__ import annotations

import json
from typing import Optional

from .config import settings

# الهوية الافتراضية للمساعد الذكي
SYSTEM_PROMPT = f"""أنت المساعد الذكي لمنظومة {settings.owner_business_name} (Schedule-ZeroBaran).
المالك: {settings.owner_name}.
بريد التواصل: {settings.owner_email}.
واتساب: {settings.owner_whatsapp}.

مهمتك:
1. الترحيب بالعملاء بأدب واحترافية.
2. مساعدتهم في فهم الخدمات المتاحة وأوقات العمل.
3. الإجابة عن أسئلتهم حول آلية الحجز والتذكيرات.
4. صياغة رسائل تأكيد وتذكير بأسلوب راقٍ ومناسب لكل عميل.
5. الالتزام بالرد بالعربية الفصحى ما لم يطلب العميل لغة أخرى.

كن مختصراً وودوداً. لا تَعِد بمواعيد أو خصومات غير موجودة."""


class AIBrain:
    """واجهة موحّدة لاستدعاء نموذج الذكاء الاصطناعي (Gemini أو Groq)."""

    def __init__(self, provider: Optional[str] = None) -> None:
        self.provider = provider or settings.ai_provider

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """يُولّد نصاً بناءً على prompt. يُرجع نصاً نظيفاً."""
        if self.provider == "gemini":
            return self._call_gemini(prompt, system or SYSTEM_PROMPT)
        if self.provider == "groq":
            return self._call_groq(prompt, system or SYSTEM_PROMPT)
        raise ValueError(f"مزود AI غير مدعوم: {self.provider}")

    # ===== Gemini =====
    def _call_gemini(self, prompt: str, system: str) -> str:
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise RuntimeError("ثبّت google-generativeai أولاً: pip install google-generativeai") from e

        if not settings.gemini_api_key:
            # وضع تجريبي بدون مفتاح
            return f"[وضع تجريبي] {prompt}"

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            settings.gemini_model,
            system_instruction=system,
        )
        try:
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            return f"⚠️ تعذّر توليد الرد عبر Gemini: {e}"

    # ===== Groq =====
    def _call_groq(self, prompt: str, system: str) -> str:
        try:
            from groq import Groq
        except ImportError as e:
            raise RuntimeError("ثبّت groq أولاً: pip install groq") from e

        if not settings.groq_api_key:
            return f"[وضع تجريبي] {prompt}"

        client = Groq(api_key=settings.groq_api_key)
        try:
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ تعذّر توليد الرد عبر Groq: {e}"


# ===== دوال مساعدة جاهزة للاستخدام =====
def craft_welcome_message(customer_name: str, services: list[str]) -> str:
    """يولّد رسالة ترحيب مخصصة للعميل."""
    services_text = "\n".join(f"• {s}" for s in services)
    prompt = (
        f"اكتب رسالة ترحيب دافئة باسم {customer_name}، واذكر الخدمات التالية:\n{services_text}\n"
        "وضّح له أنه يستطيع حجز موعد بضغطة زر، وأنه سيصله تأكيد فوري وتذكير قبل الموعد."
    )
    return AIBrain().generate(prompt)


def craft_confirmation_message(
    customer_name: str,
    service_name: str,
    start_time: str,
    meeting_url: str,
) -> str:
    """يولّد رسالة تأكيد احترافية للحجز."""
    prompt = (
        f"اكتب رسالة تأكيد حجز موعد للعميل {customer_name}.\n"
        f"الخدمة: {service_name}\n"
        f"الموعد: {start_time}\n"
        f"رابط اللقاء: {meeting_url}\n"
        "الرسالة يجب أن تكون ودّية واحترافية، وتشمل تذكيراً بأنه ستصل تذكيرات قبل الموعد."
    )
    return AIBrain().generate(prompt)


def answer_customer_question(question: str, services: list[str]) -> str:
    """يجيب عن استفسار العميل حول الخدمات أو آلية الحجز."""
    services_text = "\n".join(f"• {s}" for s in services)
    prompt = (
        f"سؤال العميل: {question}\n\n"
        f"الخدمات المتاحة:\n{services_text}\n\n"
        "أجب بإيجاز ووضوح، وأرشد العميل للحجز عبر الرابط أو البوت."
    )
    return AIBrain().generate(prompt)


def extract_appointment_intent(text: str) -> dict:
    """
    يحاول استخلاص نية الحجز من نص حرّ للعميل.
    يُرجع قاموساً يحوي: service_name, preferred_date, preferred_time.
    """
    prompt = (
        f"من النص التالي للعميل، استخلص: الخدمة المطلوبة، التاريخ المفضّل، الوقت المفضل.\n"
        f"أعد النتيجة بصيغة JSON فقط بدون شرح.\n"
        f'الحقول: service_name, preferred_date (YYYY-MM-DD), preferred_time (HH:MM).\n\n'
        f"نص العميل: {text}"
    )
    raw = AIBrain().generate(prompt)
    try:
        # محاولة استخلاص JSON من الرد
        if "{" in raw and "}" in raw:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
    except Exception:
        pass
    return {"raw": raw}
