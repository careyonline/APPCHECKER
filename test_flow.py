import os
import sys
import django

# Set UTF-8 encoding for standard output if supported
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appcheck_project.settings')
django.setup()

from django.test import Client
from appcheck.models import AppCheckRecord

def test_full_flow():
    client = Client()
    
    # 1. Test Home Page
    print("Testing Home page GET / ...")
    resp = client.get('/')
    assert resp.status_code == 200, f"Home page failed with {resp.status_code}"
    assert b"AppCheck" in resp.content
    print("  [PASS] Home page OK")
    
    # 2. Test Check Form GET
    print("Testing Check App GET /check/ ...")
    resp = client.get('/check/')
    assert resp.status_code == 200, f"Check page failed with {resp.status_code}"
    assert b"Check an App" in resp.content
    print("  [PASS] Check page OK")
    
    # 3. Test Check Form POST for Genuine App
    print("Testing Check App POST for Genuine app ...")
    genuine_payload = {
        'appName': 'Signal Private Messenger',
        'devName': 'Signal Foundation',
        'appRating': '4.7',
        'downloads': '50M+',
        'reviews': '1500000',
        'appAge': 'veteran',
        'numPermissions': '16',
        'sensitivePermissions': 'Camera, Microphone, Contacts',
        'devVerified': 'on',
        'privacyPolicy': 'on',
        'suspiciousWords': '',
        'userReviews': 'Best open source private chat app.',
    }
    resp = client.post('/check/', genuine_payload, follow=True)
    assert resp.status_code == 200
    assert b"Genuine" in resp.content
    assert b"Signal Private Messenger" in resp.content
    print("  [PASS] Genuine app prediction and result page OK")
    
    # 4. Test Check Form POST for Suspicious App
    print("Testing Check App POST for Suspicious app ...")
    fake_payload = {
        'appName': 'Free Cash Generator 9999',
        'devName': 'DarkScamHack Dev',
        'appRating': '1.8',
        'downloads': '100',
        'reviews': '5',
        'appAge': 'new',
        'numPermissions': '35',
        'sensitivePermissions': 'SMS, Contacts, Device Admin, Accessibility, Phone',
        'devVerified': 'off',
        'privacyPolicy': 'off',
        'suspiciousWords': 'scam, fake, steal, malware, stolen money',
        'userReviews': 'Fake app! It stole my info and keeps showing ads!',
    }
    resp = client.post('/check/', fake_payload, follow=True)
    assert resp.status_code == 200
    assert b"Suspicious" in resp.content
    assert b"Free Cash Generator 9999" in resp.content
    print("  [PASS] Suspicious app prediction and result page OK")
    
    # 5. Test Past Checks Page
    print("Testing Past Checks GET /past-checks/ ...")
    resp = client.get('/past-checks/')
    assert resp.status_code == 200
    assert b"Past Checks" in resp.content
    assert b"Signal Private Messenger" in resp.content
    assert b"Free Cash Generator 9999" in resp.content
    print("  [PASS] Past Checks history table OK")
    
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    test_full_flow()
