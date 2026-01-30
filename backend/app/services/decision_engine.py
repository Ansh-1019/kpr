def make_decision(media_type: str, analysis: dict):
    """
    Combines signals and produces a final verification decision.
    """

    score = 0
    reasons = []

    # -------- IMAGE / PDF LOGIC --------
    if media_type in ["image", "pdf"]:
        # 1. Forensic Text Analysis (New Logic)
        forensic_report = analysis.get("forensic_report", "")
        if forensic_report:
            # Heuristic: Scan for negative indicators in the report
            # The LLM is neutral, but if it mentions these terms, it's a signal.
            indicators = [
                "over-smoothing", "plastic-like", "inconsistent sharpness",
                "warped edges", "unnatural transitions", "asymmetric shapes",
                "mismatched light", "inconsistent reflections", "implausible details",
                "checkerboard", "grid-like artifacts", "repeating micro-patterns", 
                "abrupt texture boundaries", "inconsistent proportions"
            ]
            
            detected_indicators = []
            for indicator in indicators:
                if indicator.lower() in forensic_report.lower():
                    score += 15 # Each indicator adds to the AI score
                    detected_indicators.append(indicator)
            
            if detected_indicators:
                 reasons.append(f"Forensic anomalies detected ({len(detected_indicators)})")

        # 2. Existing Metadata Logic
        if analysis.get("qr_detected"):
            score += 40
            reasons.append("QR code detected")

        ocr_text = analysis.get("ocr_text", "")
        if ocr_text and len(ocr_text) > 100:
            score += 30
            reasons.append("Readable text extracted")

        metadata = analysis.get("metadata", {})
        if metadata:
            score += 10
            reasons.append("Metadata present")

    # -------- VIDEO LOGIC --------
    if media_type == "video":
        duration = analysis.get("duration_seconds", 0)
        if duration and duration > 5:
            score += 40
            reasons.append("Sufficient video duration")

        frames = analysis.get("sample_frames_extracted", 0)
        if frames >= 3:
            score += 30
            reasons.append("Multiple frames extracted")

    # -------- FINAL DECISION --------
    if score >= 70:
        status = "VERIFIED"
    elif score >= 40:
        status = "SUSPICIOUS"
    else:
        status = "NOT_VERIFIED"

    confidence = round(score / 100, 2)

    return {
        "status": status,
        "confidence": confidence,
        "reasons": reasons
    }
