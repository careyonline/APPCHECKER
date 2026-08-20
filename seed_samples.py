import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appcheck_project.settings')
django.setup()

from appcheck.models import AppCheckRecord
from appcheck.ml.predictor import predict_app

def seed():
    sample_apps = [
        {
            'appName': 'SecureVault Pro',
            'devName': 'SecureVault Security Corp.',
            'appRating': 4.8,
            'downloads': '10M+',
            'reviews': 240000,
            'appAge': 'veteran',
            'numPermissions': 8,
            'sensitivePermissions': 'Storage',
            'devVerified': 'on',
            'privacyPolicy': 'on',
            'suspiciousWords': '',
            'userReviews': 'Very secure application. Encrypts everything properly and easy to use.',
        },
        {
            'appName': 'Flappy Bird Premium 2024',
            'devName': 'FreeGamez Studio Ltd',
            'appRating': 2.1,
            'downloads': '500',
            'reviews': 12,
            'appAge': 'new',
            'numPermissions': 32,
            'sensitivePermissions': 'SMS, Contacts, Camera, Location, Phone',
            'devVerified': 'off',
            'privacyPolicy': 'off',
            'suspiciousWords': 'scam, virus, crash, charges money, steals data',
            'userReviews': 'Do not install! It asks for SMS permissions and keeps draining my battery!',
        },
        {
            'appName': 'CalcMaster Plus',
            'devName': 'MathTech Solutions',
            'appRating': 4.6,
            'downloads': '5M+',
            'reviews': 85000,
            'appAge': 'established',
            'numPermissions': 5,
            'sensitivePermissions': '',
            'devVerified': 'on',
            'privacyPolicy': 'on',
            'suspiciousWords': '',
            'userReviews': 'Great scientific calculator, works completely offline.',
        },
        {
            'appName': 'QuickChat Messenger',
            'devName': 'QuickChat Global Inc.',
            'appRating': 4.5,
            'downloads': '50M+',
            'reviews': 1200000,
            'appAge': 'veteran',
            'numPermissions': 18,
            'sensitivePermissions': 'Camera, Microphone, Contacts',
            'devVerified': 'on',
            'privacyPolicy': 'on',
            'suspiciousWords': '',
            'userReviews': 'Reliable messaging app with end-to-end encryption.',
        },
    ]

    for app in sample_apps:
        res = predict_app(app)
        AppCheckRecord.objects.create(
            app_name=app['appName'],
            dev_name=app['devName'],
            app_rating=app['appRating'],
            downloads=app['downloads'],
            downloads_numeric=res['downloads_numeric'],
            reviews_count=app['reviews'],
            app_age=app['appAge'],
            num_permissions=app['numPermissions'],
            sensitive_permissions=app['sensitivePermissions'],
            dev_verified=app['devVerified'] == 'on',
            privacy_policy=app['privacyPolicy'] == 'on',
            suspicious_words=app['suspiciousWords'],
            user_reviews=app['userReviews'],
            prediction=res['prediction'],
            confidence=res['confidence'],
            risk_level=res['risk_level'],
            reasons=res['reasons'],
        )
    print(f"Successfully seeded {len(sample_apps)} records into SQLite database.")

if __name__ == '__main__':
    seed()
