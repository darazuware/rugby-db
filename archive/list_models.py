import os
from google import genai

api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCA5Ke0DXp5Q15oJ44fD1BdLsjluRIv7d0')
client = genai.Client(api_key=api_key)

print("Available models:")
for model in client.models.list():
    print(f"  - {model.name}")
