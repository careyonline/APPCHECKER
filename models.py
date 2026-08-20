from django.db import models


class AppCheckRecord(models.Model):
    """A single app-safety check submitted through the /check/ form."""

    APP_AGE_CHOICES = [
        ("new", "Less than 6 months"),
        ("recent", "6 months - 1 year"),
        ("established", "1 - 3 years"),
        ("veteran", "More than 3 years"),
    ]

    PREDICTION_CHOICES = [
        ("Genuine", "Genuine"),
        ("Suspicious", "Suspicious"),
    ]

    RISK_CHOICES = [
        ("Low", "Low"),
        ("Moderate", "Moderate"),
        ("High", "High"),
    ]

    # --- Basic info ---------------------------------------------------
    app_name = models.CharField(max_length=255)
    dev_name = models.CharField(max_length=255, blank=True)

    # --- Metrics --------------------------------------------------------
    app_rating = models.FloatField(null=True, blank=True)
    downloads = models.CharField(max_length=50, blank=True)          # raw text, e.g. "50M+"
    downloads_numeric = models.BigIntegerField(default=0)             # parsed numeric value
    reviews_count = models.BigIntegerField(default=0)
    app_age = models.CharField(max_length=20, choices=APP_AGE_CHOICES, blank=True)

    # --- Security / permissions -----------------------------------------
    num_permissions = models.IntegerField(default=0)
    sensitive_permissions = models.CharField(max_length=500, blank=True)
    dev_verified = models.BooleanField(default=False)
    privacy_policy = models.BooleanField(default=False)

    # --- Reviews analysis -------------------------------------------------
    suspicious_words = models.CharField(max_length=500, blank=True)
    user_reviews = models.TextField(blank=True)

    # --- Result -----------------------------------------------------------
    prediction = models.CharField(max_length=20, choices=PREDICTION_CHOICES)
    confidence = models.IntegerField(default=0)                       # 0 - 100
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES)
    reasons = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.app_name} - {self.prediction} ({self.confidence}%)"
