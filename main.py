from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

app = FastAPI()

# 🔐 إعداد مفتاح OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧠 الدالة التي ترسل الطلب إلى GPT
def ask_gpt(prompt):
    try:
        res = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return res.choices[0].text.strip()
    except Exception as e:
        print(f"❌ GPT Error: {e}")
        return "عذرًا، حدث خطأ أثناء المعالجة."

@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()

    if SpeechResult:
        print(f"[👤] {From} قال: {SpeechResult}")
        reply = ask_gpt(SpeechResult)
        response.say(reply, language="ar-SA")
    else:
        gather = Gather(
            input="speech",
            action="/call",
            method="POST",
            language="ar-SA",
            timeout=5
        )
        gather.say("مرحباً بك، كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، إلى اللقاء.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")

@app.get("/")
def root():
    return {"status": "OK"}
