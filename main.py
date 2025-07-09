from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import google.generativeai as genai
import os

# إعداد مفتاح Gemini API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# إنشاء نموذج دردشة من Gemini (تأكد أن الاسم متاح في مشروعك)
model = genai.GenerativeModel("models/gemini-1.5-pro")

app = FastAPI()

@app.get("/call")
@app.head("/call")
async def verify_call():
    return Response(content="OK", media_type="text/plain")

@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()

    if SpeechResult:
        print(f"🔔 مكالمة جديدة من: {From} | Call SID: {CallSid}")
        print(f"🎙️ SpeechResult = {SpeechResult}")
        try:
            gpt_reply = ask_gemini(SpeechResult)
            print(f"🤖 رد Gemini: {gpt_reply}")
            response.say(gpt_reply, language="ar-SA")
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            response.say("عذرًا، حدث خطأ أثناء المعالجة. حاول لاحقًا.", language="ar-SA")
    else:
        print("⚠️ لم يتم التقاط أي كلام من المستخدم.")
        gather = Gather(input="speech", action="/call", method="POST", language="ar-SA", timeout=5)
        gather.say("مرحباً بك، أخبرني كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، يرجى المحاولة لاحقاً.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")

def ask_gemini(prompt):
    chat = model.start_chat()
    result = chat.send_message(prompt)
    return result.text.strip()
