from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .ml.predictor import predict_app
from .models import AppCheckRecord


def home(request):
    total_checks = AppCheckRecord.objects.count()
    genuine_count = AppCheckRecord.objects.filter(prediction="Genuine").count()
    suspicious_count = AppCheckRecord.objects.filter(prediction="Suspicious").count()
    recent_checks = AppCheckRecord.objects.all()[:4]

    context = {
        "total_checks": total_checks,
        "genuine_count": genuine_count,
        "suspicious_count": suspicious_count,
        "recent_checks": recent_checks,
    }
    return render(request, "appcheck/home.html", context)


def check_app(request):
    if request.method == "POST":
        form_data = request.POST

        app_name = (form_data.get("appName") or "").strip()
        if not app_name:
            messages.error(request, "App Name is required.")
            return render(request, "appcheck/check_app.html", {"form_data": form_data})

        payload = {
            "appName": app_name,
            "devName": form_data.get("devName", ""),
            "appRating": form_data.get("appRating", ""),
            "downloads": form_data.get("downloads", ""),
            "reviews": form_data.get("reviews", ""),
            "appAge": form_data.get("appAge", ""),
            "numPermissions": form_data.get("numPermissions", ""),
            "sensitivePermissions": form_data.get("sensitivePermissions", ""),
            "devVerified": form_data.get("devVerified", ""),
            "privacyPolicy": form_data.get("privacyPolicy", ""),
            "suspiciousWords": form_data.get("suspiciousWords", ""),
            "userReviews": form_data.get("userReviews", ""),
        }

        result = predict_app(payload)

        try:
            app_rating = float(payload["appRating"]) if payload["appRating"] else None
        except ValueError:
            app_rating = None

        try:
            reviews_count = int(float(payload["reviews"])) if payload["reviews"] else 0
        except ValueError:
            reviews_count = 0

        try:
            num_permissions = int(float(payload["numPermissions"])) if payload["numPermissions"] else 0
        except ValueError:
            num_permissions = 0

        record = AppCheckRecord.objects.create(
            app_name=payload["appName"],
            dev_name=payload["devName"],
            app_rating=app_rating,
            downloads=payload["downloads"],
            downloads_numeric=result["downloads_numeric"],
            reviews_count=reviews_count,
            app_age=payload["appAge"],
            num_permissions=num_permissions,
            sensitive_permissions=payload["sensitivePermissions"],
            dev_verified=payload["devVerified"] in ("on", "true", "True", True),
            privacy_policy=payload["privacyPolicy"] in ("on", "true", "True", True),
            suspicious_words=payload["suspiciousWords"],
            user_reviews=payload["userReviews"],
            prediction=result["prediction"],
            confidence=result["confidence"],
            risk_level=result["risk_level"],
            reasons=result["reasons"],
        )

        return redirect("appcheck:result", pk=record.pk)

    return render(request, "appcheck/check_app.html")


def result(request, pk):
    record = get_object_or_404(AppCheckRecord, pk=pk)
    return render(request, "appcheck/result.html", {"record": record})


def past_checks(request):
    query = (request.GET.get("q") or "").strip()
    records = AppCheckRecord.objects.all()
    if query:
        records = records.filter(app_name__icontains=query)
    return render(request, "appcheck/past_checks.html", {"records": records, "query": query})
