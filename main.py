from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

# ضع مفتاحك من OpenAI هنا أو استخدم متغير بيئة
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

app = FastAPI()

@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()

    if SpeechResult:
        print(f"[{CallSid}] - المستخدم قال: {SpeechResult}")
        gpt_reply = ask_gpt(SpeechResult)
        response.say(gpt_reply, language="ar-SA")
    else:
        gather = Gather(input="speech", action="/call", method="POST", language="ar-SA", timeout=5)
        gather.say("مرحباً بك، أخبرني كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، يرجى المحاولة لاحقاً.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")

def ask_gpt(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد صوتي ذكي لخدمة العملاء."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Error:", str(e))
        return "عذرًا، حدث خطأ أثناء المعالجة. حاول لاحقًا."