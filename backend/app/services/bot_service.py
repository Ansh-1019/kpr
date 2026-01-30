import os
import io
import json
import asyncio
import filetype
import pdfplumber
import re
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# --- Configuration & State ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

# Initialize AI Client if Key is Present
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[WARNING] AI Client Initialization Failed: {e}")

# --- Helper Logic (Rule-Based) ---

class RuleEngine:
    """
    Deterministic verification logic.
    No AI, No external calls.
    """
    
    PLATFORMS = {
        "Udemy": {
            "keywords": ["Certificate of Completion", "Udemy", "Instructor"],
            "regex": r"udemy\.com/certificate/UC-[a-zA-Z0-9-]+"
        },
        "Coursera": {
            "keywords": ["Coursera", "has successfully completed", "Verify at"],
            "regex": r"coursera\.org/account/accomplishments"
        }
    }

    @staticmethod
    def identify_platform(text: str) -> str:
        """Identify platform based on keyword density."""
        text_lower = text.lower()
        scores = {}
        for platform, rules in RuleEngine.PLATFORMS.items():
            count = sum(1 for kw in rules["keywords"] if kw.lower() in text_lower)
            scores[platform] = count
        
        # Return platform with most hits, if meaningful
        best_match = max(scores, key=scores.get)
        if scores[best_match] > 0:
            return best_match
        return "Unknown"

    @staticmethod
    def verify_rules(text: str, platform: str) -> dict:
        """
        Apply structural and content rules. 
        Returns status and reasons list.
        """
        reasons = []
        status = "Unverified"
        
        if len(text) < 50:
            return {"status": "Inconclusive", "reasons": ["Text content too short or unreadable."]}

        if platform == "Unknown":
            return {"status": "Unsupported", "reasons": ["Certificate verification is only supported for Udemy and Coursera."]}

        # Check for specific platform keywords
        rules = RuleEngine.PLATFORMS.get(platform, {})
        found = [kw for kw in rules.get("keywords", []) if kw.lower() in text.lower()]
        missing = [kw for kw in rules.get("keywords", []) if kw.lower() not in text.lower()]

        if found:
            reasons.append(f"Found required {platform} terminology: {', '.join(found)}.")
        if missing:
            reasons.append(f"Missing expected terminology: {', '.join(missing)}.")

        # ID Check (Heuristic)
        # Udemy: UC-xxxx, Coursera: 12+ chars alphanumeric
        id_found = False
        if platform == "Udemy" and "UC-" in text:
            id_found = True
            reasons.append("Certificate ID pattern (UC-) detected.")
        elif platform == "Coursera" and re.search(r"[a-zA-Z0-9]{10,}", text):
            # Very loose heuristic for Coursera IDs
             pass 

        # Final Rule-Based Status Derivation
        # We DO NOT use confidence scores. We use logical states.
        if not missing and id_found:
            status = "Consistent"
        elif found:
            status = "Partial Match"
        else:
            status = "Inconsistent"

        return {
            "status": status,
            "reasons": reasons
        }

# --- Core Service Functions ---

def _scrape_with_playwright(url: str) -> str:
    """
    Synchronous helper to scrape with Playwright.
    Must be run in a thread to avoid blocking the async event loop.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # Mimic real user agent
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            try:
                response = page.goto(url, timeout=30000)
                status_code = response.status
            except Exception as e:
                # If navigation fails (e.g. invalid domain), return generic error text
                return ""

            if status_code == 200:
                try:
                    page.wait_for_timeout(2000)
                except:
                    pass
                
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                # Extract clean text
                text = soup.get_text(separator=' ', strip=True)[:5000]
                return text
            else:
                 return ""
        except Exception as e:
            print(f"[ERROR] Playwright Scraping: {e}")
            return ""
        finally:
            browser.close()

async def verify_certificate(url: str):
    """
    Verifies a certificate URL using RuleEngine + Optional AI.
    """
    # 1. Regex Validation (Fast Fail)
    # Check against known patterns in RuleEngine
    matched_platform = "Unknown"
    for platform, rules in RuleEngine.PLATFORMS.items():
         if re.search(rules["regex"], url):
             matched_platform = platform
             break
    
    if matched_platform == "Unknown":
         # Try generic domain check
         if "udemy.com" in url: matched_platform = "Udemy"
         elif "coursera.org" in url: matched_platform = "Coursera"
         else:
             return {
                 "valid": False, "provider": "Unknown", 
                 "details": "URL does not match supported platforms (Udemy, Coursera)."
             }

    # 2. Scrape Text
    scraped_text = await asyncio.to_thread(_scrape_with_playwright, url)

    if not scraped_text:
         return {
             "valid": False, "provider": matched_platform,
             "details": "Could not retrieve page content. The link may be invalid or expired."
         }

    # 3. Rule-Based Verification
    rule_result = RuleEngine.verify_rules(scraped_text, matched_platform)
    
    # 4. Optional AI Analysis
    ai_analysis = None
    if client:
        try:
            prompt = f"""
            You are a privacy-first assistant.
            Analyze this certificate text from {matched_platform}.
            
            TEXT CONTEXT:
            {scraped_text}
            
            TASK:
            - Provide observations on consistency and typical phrasing.
            - Do NOT provide a verdict.
            
            OUTPUT: JSON with 'observations' list.
            """
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            try:
                clean = response.text.replace("```json", "").replace("```", "").strip()
                ai_analysis = json.loads(clean)
            except:
                ai_analysis = {"raw_notes": response.text}
        except:
            pass # Fail open/silently for AI

    # 5. Construct Response (Backwards Compatible)
    is_valid = rule_result["status"] in ["Consistent", "Partial Match"]
    
    # Detailed message
    details = f"Status: {rule_result['status']}\n"
    details += "\n".join([f"- {r}" for r in rule_result["reasons"]])
    
    if ai_analysis:
        obs = ai_analysis.get("observations", [])
        if obs:
            details += "\n\nAI Observations:\n" + "\n".join([f"- {o}" for o in obs])

    return {
        "valid": is_valid,
        "provider": matched_platform,
        "details": details,
        # New structure included for future frontend updates:
        "structured_analysis": {
            "platform": matched_platform,
            "rule_result": rule_result,
            "ai_analysis": ai_analysis
        }
    }

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"[ERROR] PDF Extraction: {e}")
        return ""

async def analyze_file_upload(file_content: bytes):
    """
    Main Entry Point for File Upload Verification.
    Orchestrates: Extract -> Rules -> Optional AI.
    """
    # 1. File Type Detection
    kind = filetype.guess(file_content)
    mime = kind.mime if kind else "application/octet-stream"
    is_pdf = "pdf" in mime
    
    extracted_text = ""
    
    # 2. Text Extraction (PDF Only for now)
    if is_pdf:
        extracted_text = await asyncio.to_thread(extract_text_from_pdf, file_content)
    else:
        # If image, we assume we cannot do Rule-Based without OCR. 
        # For this architecture, we skip Rule-Based text checks for images or handle minimally.
        extracted_text = "" 

    # 3. Rule-Based Verification (No API Key Required)
    platform = RuleEngine.identify_platform(extracted_text)
    rule_result = RuleEngine.verify_rules(extracted_text, platform)

    # 4. AI Assist (Optional)
    ai_analysis = None
    ai_message = "AI analysis skipped (API Key missing)."

    # Only call AI if we have a client AND (it's a PDF OR an Image)
    if client:
        try:
            ai_message = "AI analysis performed."
            
            # Prepare content for Gemini
            media_part = None
            if is_pdf:
                media_part = types.Part.from_bytes(data=file_content, mime_type="application/pdf")
            elif "image" in mime:
                img = Image.open(io.BytesIO(file_content))
                media_part = img
            
            if media_part:
                prompt = """
                You are a privacy-first assistant for certificate analysis.
                
                ROLE:
                - Provide OBSERVATIONS ONLY.
                - Do NOT declare "Real" or "Fake".
                - Do NOT give scores.
                
                TASK:
                - Check for visual consistency with Udemy/Coursera.
                - Note any formatting anomalies.
                
                OUTPUT format: JSON with keys 'observations' (list) and 'concerns' (list).
                """
                
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[prompt, media_part]
                )
                
                # Try to parse strict JSON if model followed instructions, else raw text
                try:
                    # Clean markdown code blocks if present
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    ai_analysis = json.loads(clean_text)
                except:
                    ai_analysis = {"raw_notes": response.text}

        except Exception as e:
            print(f"[ERROR] AI Call Failed: {e}")
            ai_message = "AI analysis failed/skipped due to error."
            ai_analysis = None

    # 5. Construct Final Response
    return {
        "platform": platform,
        "rule_based_result": rule_result,
        "ai_analysis": ai_analysis,
        "message": ai_message
    }


# Backwards compatibility wrapper for API router if needed
async def analyze_image_with_gemini(file_content: bytes):
    """
    Wrapper to match the signature expected by api/bot.py.
    Returns JSON string as expected by the existing router.
    """
    result = await analyze_file_upload(file_content)
    return json.dumps(result)
