# from google import genai (Already imported or need to change import)
# Re-importing correctly inside the function or file level
import os
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from fastapi import HTTPException
from PIL import Image
import io
import re
import asyncio
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini
# Note: GEMINI_API_KEY must be set in environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Client initialization is best done once or per request if stateless
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

async def analyze_image_with_gemini(file_content: bytes):
    """
    Analyzes an image to determine if it's AI-generated or real using Gemini Flash.
    """
    print(f"[DEBUG] Starting analysis. Image size: {len(file_content)} bytes")
    
    if not client:
        print("[ERROR] Gemini Client not initialized. Check GEMINI_API_KEY.")
        # Return a JSON string that the frontend can parse as an error explanation
        return '{"is_ai": false, "confidence": 0.0, "reasoning": "System Error: Gemini API Key is missing or invalid. Please check backend configuration."}'

    try:
        image = Image.open(io.BytesIO(file_content))
        
        prompt = """
        Analyze the provided image strictly from a forensic and observational perspective.

        Focus ONLY on visually observable characteristics, including:

        1. Texture & Detail Characteristics
           - Over-smoothing or plastic-like surfaces
           - Loss of fine-grain noise typically produced by camera sensors
           - Inconsistent sharpness across different regions

        2. Structural & Geometric Coherence
           - Irregular or asymmetric shapes
           - Warped edges or unnatural transitions
           - Inconsistent proportions or alignment

        3. Lighting, Shadows & Reflections
           - Light direction inconsistencies
           - Shadows that do not align with objects
           - Implausible reflections or highlights

        4. Pattern Repetition & Artifacts
           - Repeating micro-patterns or textures
           - Grid-like or checkerboard artifacts
           - Abrupt texture boundaries

        5. Overall Visual Plausibility
           - Details that appear realistic individually but inconsistent together
           - Subtle anomalies that warrant closer inspection

        IMPORTANT RULES:
        - Do NOT label the image as “real”, “fake”, or “AI-generated”.
        - Do NOT use absolute or definitive language.
        - Do NOT assign numeric scores or probabilities.
        - Keep language neutral, descriptive, and evidence-based.

        OUTPUT FORMAT (STRICT):
        Return your analysis using the following structure:

        Observations:
        - Bullet-point list of notable visual characteristics.

        Potential Synthetic Indicators:
        - Visual traits that are commonly associated with synthetic or algorithmically generated imagery.

        Uncertainty & Limitations:
        - Factors that limit confidence or make the analysis inconclusive.

        Explanation Summary:
        - A short, neutral explanation suitable for end users, describing why the system flagged certain aspects for further verification.
        """
        
        print("[DEBUG] Sending request to Gemini (google-genai)...")
        
        # New SDK usage
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, image]
        )
        
        print(f"[DEBUG] Gemini Response received.")
        
        if not response.text:
            print("[ERROR] No text returned")
            raise ValueError("Model returned no text.")

        # Raw Forensic Report
        forensic_report = response.text.strip()
        print(f"[DEBUG] Raw Report Length: {len(forensic_report)}")
        
        # DECISION ENGINE INTEGRATION
        # The LLM gives the report, the Decision Engine gives the verdict.
        from app.services.decision_engine import make_decision
        
        # Prepare analysis object for the engine
        analysis_data = {
            "forensic_report": forensic_report,
            "metadata": {}, # Could be populated by a separate metadata extractor
            "qr_detected": False, # Placeholder
            "ocr_text": ""     # Placeholder
        }
        
        decision = make_decision("image", analysis_data)
        
        # Mapping Decision Engine status to Frontend "is_ai" boolean
        # decision['status'] is VERIFIED (Real), SUSPICIOUS (AI/Fake), NOT_VERIFIED
        is_ai = False
        if decision['status'] == 'SUSPICIOUS':
            is_ai = True
            
        result = {
            "is_ai": is_ai, 
            "confidence": decision['confidence'], 
            "reasoning": forensic_report
        }
        return json.dumps(result) 

    except Exception as e:
        print(f"[ERROR] Exception in Gemini analysis: {e}")
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
             return '{"error": true, "title": "Service Currently Busy", "message": "Our advanced forensic analysis service is currently experiencing unusually high demand.\\n\\nPlease rest assured that your submission was processed securely and has not been stored or retained.\\n\\nWe recommend waiting a brief moment before attempting your verification again."}'
        
        return f'{{"error": true, "title": "Analysis Failed", "message": "{error_msg.replace('"', "'")}"}}'



def _scrape_with_playwright(url):
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
            response = page.goto(url, timeout=30000)
            status_code = response.status
            print(f"[DEBUG] Playwright Status: {status_code}")
            
            if status_code == 200:
                # Wait a bit for dynamic content
                try:
                    page.wait_for_timeout(2000)
                except:
                    pass
                
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)[:3000]
                return text
            else:
                 return f"Could not retrieve page content. Status: {status_code}"
        finally:
            browser.close()

async def verify_certificate(url: str):
    """
    Verifies a certificate URL using AI analysis + Rule Engine.
    """
    try:
        # 1. Regex / Format Check
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        provider = "Unknown"
        url_valid = False
        
        if "udemy.com" in url:
            provider = "Udemy"
            udemy_pattern = r"udemy\.com/certificate/UC-[a-zA-Z0-9-]+"
            if re.search(udemy_pattern, url):
                url_valid = True
        elif "coursera.org" in url:
            provider = "Coursera"
            coursera_pattern = r"coursera\.org/account/accomplishments/(verify|certificate)/[a-zA-Z0-9]+"
            if re.search(coursera_pattern, url):
                 url_valid = True

        if not url_valid:
             return {"valid": False, "provider": provider, "details": "Invalid URL format or unsupported provider."}

        # 2. Text Extraction (Scraping)
        scraped_text = ""
        try:
             print(f"[DEBUG] Launching Playwright (Sync) for {url}...")
             # Run synchronous playwright in a separate thread
             scraped_text = await asyncio.to_thread(_scrape_with_playwright, url)
                    
        except Exception as scrap_err:
             print(f"[ERROR] Scraping failed: {scrap_err}")
             scraped_text = f"Scraping failed: {str(scrap_err)}"

        # 3. AI Forensic Analysis
        prompt = f"""
        Analyze the provided certificate text strictly as a verification assistant.
        
        Certificate Text Context:
        {scraped_text}
        
        Focus on the following observable aspects:

        1. Platform-Specific Structure
           - Presence of known {provider} branding concepts
           - Typical terminology used by the platform ("Certificate of Completion", etc.)

        2. Certificate Identifiers
           - Presence of certificate ID or verification code in the text
           - Format consistency

        3. Content Consistency
           - Logical consistency between Name, Course, and Issuer
           
        4. Visual & Formatting Quality (Inferred from text structure)
           - Coherence of extracted text info

        5. Verification Limitations
           - Whether authenticity can be reasonably assessed from text only

        IMPORTANT RULES:
        - Do NOT declare the certificate as authentic or fake.
        - Do NOT assign numeric confidence scores.
        - Do NOT imply legal or official verification.
        - Use neutral, descriptive language only.

        OUTPUT FORMAT (STRICT):
        Return your analysis using the following structure:

        Platform Identification:
        - Detected platform ({provider} based on text analysis).

        Observations:
        - Bullet points describing notable structural or textual characteristics.

        Potential Concerns:
        - Aspects that may require further verification or raise uncertainty.

        Verification Indicators:
        - Features that are commonly expected in genuine certificates.

        Uncertainty & Limitations:
        - Reasons why a definitive conclusion cannot be made.

        Explanation Summary:
        - A short, neutral explanation suitable for end users.
        """
        
        print("[DEBUG] Sending Certificate Analysis to Gemini...")
        
        # We use generate_content with TEXT (not image)
        ai_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        forensic_report = ai_response.text.strip() if ai_response.text else "AI Analysis failed to generate report."

        # 4. Decision Engine Verdict
        from app.services.decision_engine import make_decision
        
        analysis_data = {
            "url_valid": url_valid,
            "provider": provider,
            "forensic_report": forensic_report
        }
        
        decision = make_decision("certificate", analysis_data)
        
        # Map to Frontend format
        return {
            "valid": decision['status'] == 'VERIFIED',
            "provider": provider,
            "details": forensic_report # We show the full report as details
        }

    except Exception as e:
        print(f"[ERROR] Cert Verify Failed: {e}")
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
             return {
                "valid": False,
                "provider": "System Busy",
                "details": "High traffic volume. Please try again in 1 minute."
             }
        return {
            "valid": False, 
            "provider": "Error", 
            "details": f"Verification failed: {error_msg}"
        }
