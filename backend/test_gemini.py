
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment variables.")
    exit(1)

print(f"✅ Found GOOGLE_API_KEY: {api_key[:5]}...{api_key[-4:]}")

try:
    genai.configure(api_key=api_key)
    print("🔄 Attempting to list available models...")
    models = list(genai.list_models())
    gemini_models = [m.name for m in models if 'gemini' in m.name]
    
    if gemini_models:
        print(f"✅ Successfully connected! Found {len(gemini_models)} Gemini models.")
        print(f"   Example: {gemini_models[0]}")
        
        # Try a simple generation
        print("🔄 Testing generation...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, can you hear me?")
        if response and response.text:
             print("✅ Generation successful!")
        else:
             print("⚠️ Connected but generation failed (no text returned).")

    else:
        print("⚠️ Connected but no Gemini models found. Check API key permissions.")

except Exception as e:
    print(f"❌ Connection Failed: {str(e)}")
