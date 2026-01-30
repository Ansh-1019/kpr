import re

class VerificationRules:
    """
    Pure deterministic rules for verifying certificates.
    No AI, No External API calls (except initial fetching).
    """

    PATTERNS = {
        "Udemy": {
            "url": r"https?://(www\.)?udemy\.com/certificate/UC-[a-zA-Z0-9-]+/?",
            "keywords": ["Certificate of Completion", "Udemy", "Instructor"],
            "negative_keywords": ["preview", "draft", "example"]
        },
        "Coursera": {
            "url": r"https?://(www\.)?coursera\.org/account/accomplishments/(verify|certificate)/[a-zA-Z0-9]+/?",
            "keywords": ["Coursera", "has successfully completed", "Verify at"],
            "negative_keywords": []
        }
    }

    @staticmethod
    def validate_url(url: str):
        """
        Checks if the URL matches known platform patterns.
        Returns: (is_valid, provider, details)
        """
        url = url.strip()
        print(f"[DEBUG] validate_url input: {repr(url)}")
        for provider, rules in VerificationRules.PATTERNS.items():
            pattern = rules["url"]
            print(f"[DEBUG] Testing pattern: {pattern}")
            if re.match(pattern, url):
                return True, provider, "URL matches official pattern."
        
        # Check if domain exists but pattern is wrong
        if "udemy.com" in url:
             return False, "Udemy", "Invalid Udemy URL format."
        if "coursera.org" in url:
             return False, "Coursera", "Invalid Coursera URL format."
             
        return False, "Unknown", "URL not recognized or supported."

    @staticmethod
    def analyze_text_content(text: str, provider: str):
        """
        Analyzes extracted text for required keywords and consistency.
        Returns: (score, observations)
        """
        score = 0
        observations = []
        
        if not text or len(text) < 50:
            return 0, ["Insufficient text content for analysis."]

        # 1. Provider Validation
        if provider in VerificationRules.PATTERNS:
            rules = VerificationRules.PATTERNS[provider]
            
            # Check for positive keywords
            found_keywords = [kw for kw in rules["keywords"] if kw.lower() in text.lower()]
            if found_keywords:
                score += 20 * len(found_keywords) # Up to 60-80 points
                observations.append(f"Found {provider} keywords: {', '.join(found_keywords)}")
            else:
                observations.append(f"Missing standard {provider} terminology.")

            # Check for negative keywords
            found_negatives = [kw for kw in rules["negative_keywords"] if kw.lower() in text.lower()]
            if found_negatives:
                score -= 100
                observations.append(f"SUSPICIOUS: Found negative keywords: {', '.join(found_negatives)}")

            # General checks
            if "certificate" in text.lower():
                 score += 10
                 observations.append("Contains 'Certificate' terminology.")
        
        else:
            observations.append("Unknown provider, skipping specific keyword checks.")

        return min(max(score, 0), 100), observations
