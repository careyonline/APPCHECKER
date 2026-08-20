"""
AppCheck prediction engine.

This module scores a submitted app on a 0-100 "genuineness" scale using a
transparent, explainable set of rule-based heuristics (developer trust
signals, review/rating patterns, permission footprint, and suspicious
language in reviews). Each factor that moves the score also produces a
human-readable "reason" string, which is what powers the "Why did we get
this result?" section on the result page.

The scoring function is intentionally isolated behind ``predict_app()`` so
that it can later be swapped out for a trained scikit-learn model (e.g. a
RandomForestClassifier persisted with joblib) without changing any of the
calling code in views.py / seed_samples.py.
"""

import re

# Permissions considered "dangerous" / privacy-sensitive on Android.
DANGEROUS_PERMISSIONS = {
    "sms", "contacts", "device admin", "accessibility", "phone", "location",
    "camera", "microphone", "storage", "call log", "calendar", "body sensors",
}

NEGATIVE_REVIEW_KEYWORDS = [
    "scam", "fake", "steal", "stole", "stolen", "virus", "malware", "hack",
    "hacked", "fraud", "crash", "crashes", "spam", "phishing", "trojan",
    "ransomware", "spyware", "bug", "broken",
]

POSITIVE_REVIEW_KEYWORDS = [
    "secure", "reliable", "great", "love", "excellent", "trust", "safe",
    "smooth", "encrypt", "private",
]


def _parse_downloads(raw: str) -> int:
    """Turn strings like '50M+', '1.2M', '500', '10K+' into an int."""
    if not raw:
        return 0
    raw = str(raw).strip().upper().replace(",", "").replace("+", "")
    match = re.match(r"^([\d.]+)\s*([KMB]?)$", raw)
    if not match:
        digits = re.sub(r"[^\d.]", "", raw)
        try:
            return int(float(digits)) if digits else 0
        except ValueError:
            return 0
    number, suffix = match.groups()
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000, "": 1}[suffix]
    try:
        return int(float(number) * multiplier)
    except ValueError:
        return 0


def _split_words(raw: str):
    if not raw:
        return []
    return [w.strip().lower() for w in raw.split(",") if w.strip()]


def predict_app(app: dict) -> dict:
    """
    Score a submitted app.

    ``app`` is expected to be a dict with keys matching the /check/ form
    field names (appName, devName, appRating, downloads, reviews, appAge,
    numPermissions, sensitivePermissions, devVerified, privacyPolicy,
    suspiciousWords, userReviews). devVerified / privacyPolicy may be the
    string "on" (as posted by an HTML checkbox) or a real bool.

    Returns a dict with: prediction, confidence, risk_level, reasons,
    downloads_numeric.
    """
    reasons = []
    score = 50  # neutral starting point out of 100

    def bump(amount, reason):
        nonlocal score
        score += amount
        reasons.append(reason)

    # --- Developer trust signals -----------------------------------------
    dev_verified = app.get("devVerified") in ("on", True, "true", "True")
    privacy_policy = app.get("privacyPolicy") in ("on", True, "true", "True")

    if dev_verified:
        bump(15, "Developer is verified")
    else:
        bump(-8, "Developer identity is not verified")

    if privacy_policy:
        bump(15, "Privacy policy is available")
    else:
        bump(-8, "No privacy policy was provided")

    # --- Rating -------------------------------------------------------------
    try:
        rating = float(app.get("appRating") or 0)
    except (TypeError, ValueError):
        rating = 0.0

    if rating >= 4.0:
        bump(10, "Strong average user rating")
    elif rating and rating < 2.5:
        bump(-15, "Very low average user rating")

    # --- Reviews volume -------------------------------------------------------
    try:
        reviews = int(float(app.get("reviews") or 0))
    except (TypeError, ValueError):
        reviews = 0

    if reviews >= 10_000:
        bump(10, "Large number of genuine-looking reviews")
    elif reviews < 50:
        bump(-10, "Very few reviews for this app")

    # --- App age --------------------------------------------------------------
    app_age = (app.get("appAge") or "").strip()
    if app_age == "veteran":
        bump(10, "Established app with a long track record")
    elif app_age == "established":
        bump(5, "App has been available for over a year")
    elif app_age == "new":
        bump(-10, "App was published very recently")

    # --- Downloads --------------------------------------------------------------
    downloads_numeric = _parse_downloads(app.get("downloads", ""))
    if downloads_numeric >= 1_000_000:
        bump(10, "Widely downloaded by other users")
    elif downloads_numeric and downloads_numeric < 1_000:
        bump(-10, "Very low download count")

    # --- Permissions ------------------------------------------------------------
    try:
        num_permissions = int(float(app.get("numPermissions") or 0))
    except (TypeError, ValueError):
        num_permissions = 0

    if num_permissions > 25:
        bump(-15, "Requests an excessive number of permissions")
    elif 0 < num_permissions <= 10:
        bump(5, "Reasonable number of permissions")

    sensitive_list = _split_words(app.get("sensitivePermissions", ""))
    if len(sensitive_list) > 2:
        extra = len(sensitive_list) - 2
        bump(-3 * extra, "Requests several sensitive permissions")
    elif sensitive_list:
        reasons.append("Requests a small set of sensitive permissions")

    # --- Suspicious words flagged explicitly by the user -------------------------
    suspicious_words = _split_words(app.get("suspiciousWords", ""))
    if suspicious_words:
        penalty = min(40, len(suspicious_words) * 8)
        bump(-penalty, "Reviewer-flagged suspicious keywords were provided")

    # --- Free-text review scan ------------------------------------------------------
    review_text = (app.get("userReviews") or "").lower()
    matched_negative = {kw for kw in NEGATIVE_REVIEW_KEYWORDS if kw in review_text}
    matched_positive = {kw for kw in POSITIVE_REVIEW_KEYWORDS if kw in review_text}

    for kw in matched_negative:
        bump(-5, f'User reviews mention "{kw}"')
    if matched_positive and not matched_negative:
        bump(3, "User reviews use positive, trustworthy language")

    # --- Finalize -------------------------------------------------------------------
    score = max(0, min(100, score))

    if score >= 55:
        prediction = "Genuine"
    else:
        prediction = "Suspicious"

    if score >= 80:
        risk_level = "Low"
    elif score >= 55:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    # Keep the most relevant handful of reasons (avoid an overwhelming list).
    reasons = reasons[:8] if reasons else ["No strong signals were detected either way."]

    return {
        "prediction": prediction,
        "confidence": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "downloads_numeric": downloads_numeric,
    }
