import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from app.services.verification_rules import VerificationRules

def test_verification_rules_regex():
    """Test the pure regex logic."""
    valid_udemy = "https://www.udemy.com/certificate/UC-123456"
    valid_coursera = "https://www.coursera.org/account/accomplishments/verify/123456"
    invalid_url = "https://example.com/certificate"
    
    print(f"Testing Udemy: {valid_udemy}")
    res_u = VerificationRules.validate_url(valid_udemy)
    print(f"Result: {res_u}")
    assert res_u[0] == True, "Udemy Regex Failed"

    print(f"Testing Coursera: {valid_coursera}")
    res_c = VerificationRules.validate_url(valid_coursera)
    assert res_c[0] == True, "Coursera Regex Failed"

    print(f"Testing Invalid: {invalid_url}")
    res_i = VerificationRules.validate_url(invalid_url)
    assert res_i[0] == False, "Invalid URL Test Failed"

def test_verification_rules_content():
    """Test the text scoring logic."""
    udemy_text = "This is a Certificate of Completion issued by Udemy to User Name."
    score, obs = VerificationRules.analyze_text_content(udemy_text, "Udemy")
    assert score > 0
    assert any("Found Udemy keywords" in o for o in obs)
    
    bad_text = "This is a random text."
    score, obs = VerificationRules.analyze_text_content(bad_text, "Udemy")
    assert score == 0
    assert any("Missing standard Udemy terminology" in o for o in obs)

if __name__ == "__main__":
    test_verification_rules_regex()
    test_verification_rules_content()
    print("ALL TESTS PASSED")
