"""Quick test to verify your Gemini API key is valid."""
import google.generativeai as genai
import sys

# Paste your key here or pass it as an argument
API_KEY = sys.argv[1] if len(sys.argv) > 1 else input("Paste your Gemini API key: ").strip()

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello in one word.")
    print(f"\n✅ SUCCESS! Your API key is valid.")
    print(f"   Gemini responded: {response.text.strip()}")
except Exception as e:
    print(f"\n❌ FAILED! Your API key is NOT valid.")
    print(f"   Error: {e}")
