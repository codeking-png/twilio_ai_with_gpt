from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

# 🔐 إعداد مفتاح OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key or openai.api_key == "YOUR_OPENAI_API_KEY":
    print("⚠️ تحذير: مفتاح OpenAI غير مفعّل. يرجى تعيين OPENAI_API_KEY في Render.")

app = FastAPI()

# 🧠 دالة السؤال لـ GPT
def ask_gpt(prompt: str) -> str:
    try:
        print(f"[GPT طلب] >> {prompt}")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        reply = response.choices[0].text.strip()
        print(f"[GPT رد] << {reply}")
        return reply
    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بـ OpenAI: {e}")
        return "حدث خطأ أثناء محاولة فهمك، يرجى المحاولة لاحقاً."

# 📞 نقطة استقبال المكالمات من Twilio
@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()

    print(f"📞 مكالمة جديدة من {From} (CallSid: {CallSid})")

    if SpeechResult:
        print(f"🗣️ المستخدم قال: {SpeechResult}")
        gpt_reply = ask_gpt(SpeechResult)
        response.say(gpt_reply, language="ar-SA")
    else:
        gather = Gather(input="speech", action="/call", method="POST", language="ar-SA", timeout=5)
        gather.say("مرحباً بك، أخبرني كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، يرجى المحاولة لاحقاً.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")
