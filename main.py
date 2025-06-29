from fastapi import FastAPI, Request, Form
from fastapi.responses import Response, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

# إعداد FastAPI
app = FastAPI()

# مفتاح OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# صفحة اختبار GET
@app.get("/")
def root():
    return {"message": "API يعمل بنجاح"}

# نقطة GET مؤقتة لتشخيص /call
@app.get("/call")
def get_call():
    return {"info": "هذه الواجهة تستقبل POST فقط من Twilio."}

# الدالة التي تتواصل مع GPT
def ask_gpt(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"❌ خطأ GPT: {e}")
        return "حدث خطأ أثناء المعالجة، يرجى المحاولة لاحقاً."

# نقطة استلام المكالمات من Twilio
@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()
    print(f"📞 مكالمة من: {From} - CallSid: {CallSid}")

    if SpeechResult:
        print(f"🗣️ قال المتصل: {SpeechResult}")
        gpt_reply = ask_gpt(SpeechResult)
        response.say(gpt_reply, language="ar-SA")
    else:
        gather = Gather(input="speech", action="/call", method="POST", language="ar-SA", timeout=5)
        gather.say("مرحباً، كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، إلى اللقاء.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")
