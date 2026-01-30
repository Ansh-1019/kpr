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
from dotenv import load_dotenv

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
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             return '{"error": true, "title": "Service Currently Busy", "message": "Our advanced forensic analysis service is currently experiencing unusually high demand.\\n\\nPlease rest assured that your submission was processed securely and has not been stored or retained.\\n\\nWe recommend waiting a brief moment before attempting your verification again."}'
        
        return f'{{"error": true, "title": "Analysis Failed", "message": "{error_msg.replace('"', "'")}"}}'



async def verify_certificate(url: str):
    """
    Verifies a certificate URL from Udemy or Coursera.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1'
        }
        
        if "udemy.com" in url:
            provider = "Udemy"
            # Strict Regex for Udemy: https://www.udemy.com/certificate/UC-xxxx/
            # Example: UC-011aea85-6526-4e68-ade5-02763e2f10a1
            udemy_pattern = r"udemy\.com/certificate/UC-[a-zA-Z0-9-]+"
            if not re.search(udemy_pattern, url):
                 return {"valid": False, "provider": provider, "details": "Invalid URL format. Expected 'udemy.com/certificate/UC-...'"}

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.string if soup.title else ""
                
                # Check for "Certificate of Completion"
                is_valid = "Certificate" in page_title or "Udemy" in response.text
                
                return {
                    "valid": is_valid,
                    "provider": provider,
                    "details": page_title.strip() if page_title else "Certificate found"
                }
            elif response.status_code == 403:
                # Fallback: Regex passed, so format is valid.
                return {
                    "valid": True,
                    "provider": provider,
                    "details": "Certificate ID format is valid. (Deep verification blocked by provider)"
                }
            else:
                 return {"valid": False, "provider": provider, "details": f"URL verification failed (Status {response.status_code})"}

        elif "coursera.org" in url:
            provider = "Coursera"
            # Coursera verify URLs: https://www.coursera.org/account/accomplishments/verify/XXXX
            # Also sometimes: https://www.coursera.org/account/accomplishments/certificate/XXXX
            if "verify" not in url and "certificate" not in url:
                return {"valid": False, "provider": provider, "details": "Invalid Coursera certificate URL format"}
            
            coursera_pattern = r"coursera\.org/account/accomplishments/(verify|certificate)/[a-zA-Z0-9]+"
            if not re.search(coursera_pattern, url):
                 return {"valid": False, "provider": provider, "details": "Invalid URL format. Expected 'coursera.org/account/accomplishments/...'"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                 soup = BeautifulSoup(response.text, 'html.parser')
                 page_title = soup.title.string if soup.title else ""
                 
                 is_valid = "Coursera" in page_title
                 return {
                    "valid": is_valid,
                    "provider": provider,
                    "details": page_title.strip() if page_title else "Certificate found"
                }
            elif response.status_code == 403:
                 return {
                    "valid": True,
                    "provider": provider,
                    "details": "Certificate ID format is valid. (Deep verification blocked by provider)"
                }
            else:
                 return {"valid": False, "provider": provider, "details": "URL verification failed"}
        else:
             return {
                "valid": False,
                "provider": "Unknown",
                "details": "Only Udemy and Coursera are supported currently"
            }

    except Exception as e:
        return {
            "valid": False, 
            "provider": "Error", 
            "details": str(e)
        }
