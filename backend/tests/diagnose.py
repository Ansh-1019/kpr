
import sys
print(f"Python Executable: {sys.executable}")
print(f"Python Path: {sys.path}")

try:
    from google import genai
    print("SUCCESS: 'from google import genai' worked.")
except ImportError as e:
    print(f"FAILURE: 'from google import genai' failed: {e}")

try:
    import google.generativeai as genai_old
    print("INFO: 'import google.generativeai' (old sdk) is availble.")
except ImportError:
    print("INFO: 'import google.generativeai' (old sdk) is NOT availble.")

import requests

def check_udemy_invalid():
    url = "https://www.udemy.com/certificate/INVALID-URL-12345/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        print(f"Checking Invalid URL: {url}")
        res = requests.get(url, headers=headers)
        print(f"Invalid URL Status Code: {res.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_udemy_invalid()
