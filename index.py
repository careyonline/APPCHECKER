"""
Vercel Python entrypoint.

Vercel's Python runtime looks for a WSGI-compatible `app` (or `handler`)
callable in this file. We simply hand it Django's WSGI application.
"""

import os
import sys
from pathlib import Path

# Make sure the project root (one level up from /api) is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appcheck_project.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
