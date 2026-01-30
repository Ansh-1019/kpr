import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from app.services.verification_rules import VerificationRules
from app.services.bot_service import verify_certificate, analyze_image_with_gemini

# Mocking Playwright and AI integration is best for unit tests, 
# but for this verification step we want to test the *rules* and *integration* logic.

def test_verification_rules_regex():
    """Test the pure regex logic."""
    valid_udemy = "https://www.udemy.com/certificate/UC-123456"
    valid_coursera = "https://www.coursera.org/account/accomplishments/verify/123456"
    invalid_url = "https://example.com/certificate"
    
    print(f"Testing Udemy: {valid_udemy}")
    res_u = VerificationRules.validate_url(valid_udemy)
    print(f"Result: {res_u}")
    assert res_u[0] == True

    print(f"Testing Coursera: {valid_coursera}")
    res_c = VerificationRules.validate_url(valid_coursera)
    print(f"Result: {res_c}")
    assert res_c[0] == True

    print(f"Testing Invalid: {invalid_url}")
    res_i = VerificationRules.validate_url(invalid_url)
    print(f"Result: {res_i}")
    assert res_i[0] == False

def test_verification_rules_content():
    """Test the text scoring logic."""
    udemy_text = "This is a Certificate of Completion issued by Udemy to User Name."
    score, obs = VerificationRules.analyze_text_content(udemy_text, "Udemy")
    assert score > 0
    assert "Found Udemy keywords" in obs[0]
    
    bad_text = "This is a random text."
    score, obs = VerificationRules.analyze_text_content(bad_text, "Udemy")
    assert score == 0
    assert any("Missing standard Udemy terminology" in o for o in obs)

async def test_analyze_file_logic():
    # Since we can't easily mock PDF bytes without a real file, we'll test the loop logic conceptually
    # by passing a non-pdf (image) and seeing if it tries to process it.
    pass 

if __name__ == "__main__":
    # Manual run wrapper
    print("Running Regex Tests...")
    test_verification_rules_regex()
    print("Regex Tests Passed.")
    
    print("Running Content Rule Tests...")
    test_verification_rules_content()
    print("Content Rule Tests Passed.")
    
    # We can also run the real verify_certificate against a known BAD url to ensure it blocks it without AI
    print("Running Live Validation Logic (Invalid URL)...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(verify_certificate("https://google.com"))
    print(f"Result for Invalid URL: {result}")
    
    assert result['valid'] == False
    assert "Analysis halted" in result['details']
    print("Live Logic Passed.")
