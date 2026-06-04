import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv("d:/Unada Task/ai-research-agent/backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
