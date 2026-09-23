#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing config import...")
try:
    from app.config import settings
    print("SUCCESS: Config imported successfully")
    print(f"App name: {settings.APP_NAME}")
    print(f"Version: {settings.VERSION}")
    print(f"Gemini API key configured: {bool(settings.GEMINI_API_KEY)}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
