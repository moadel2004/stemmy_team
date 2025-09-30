import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
project = os.getenv("OPENAI_PROJECT") # السطر ده هيقرأ البروجكت من ملف .env

# هنا التعديل المهم
client = OpenAI(
    api_key=api_key,
    project=project  # احنا ضفنا السطر ده عشان نبعت البروجكت مع الطلب
)

try:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":"hi"}],
        temperature=0
    )
    print("OK:", r.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
