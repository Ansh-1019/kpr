
import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

print("Listing models...")
try:
    with open('models.txt', 'w') as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                f.write(m.name + '\n')
except Exception as e:
    print(f"Error listing models: {e}")
