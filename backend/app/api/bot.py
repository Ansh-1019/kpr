
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.bot_service import analyze_image_with_gemini, verify_certificate
import json

router = APIRouter()

class CertificateRequest(BaseModel):
    url: str

@router.post("/bot/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    print(f"[DEBUG] API received file: {file.filename}")

    # Read file content
    content = await file.read()
    
    # Process with Gemini
    # The service returns a JSON string, we try to parse it to return a proper JSON object
    try:
        result_str = await analyze_image_with_gemini(content)
        print(f"[DEBUG] Service returned result string of length {len(result_str)}")
    except Exception as e:
        print(f"[ERROR] Service call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        result_json = json.loads(result_str)
        print(f"[DEBUG] JSON Parsed successfully. returning.")
        return result_json
    except json.JSONDecodeError as e:
        # If parsing fails, return raw string (or wrap it)
        print(f"[ERROR] JSON Decode Error: {e}. Raw: {result_str}")
        return {
            "raw_response": result_str,
            "note": "Could not parse JSON from AI model"
        }

@router.post("/bot/verify-certificate")
async def verify_cert_endpoint(request: CertificateRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    result = await verify_certificate(request.url)
    return result
