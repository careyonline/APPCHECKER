# 🛡️ AppCheck - Intelligent App Safety & Risk Assessment

AppCheck is a Django web application that evaluates mobile apps for security risks, intrusive permissions, malware indicators, and deceptive behaviors using explainable, rule-based heuristics.

---

## 🚀 Features

- **App Safety Scoring & Risk Classification**: Classifies apps into Genuine or Suspicious, with a Low / Moderate / High risk level and a 0-100% confidence score.
- **Detailed Permission Breakdown**: Flags excessive or unusually sensitive permission requests.
- **Explainable Analysis**: Highlights the specific factors that drove the result (developer verification, privacy policy, rating, review volume, suspicious review language, etc).
- **History & Past Checks**: Search and review previously scanned applications.
- **Modern, responsive UI**: Clean light-mode design built with Tailwind CSS.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Django
- **Prediction engine**: Explainable rule-based scoring (`appcheck/ml/predictor.py`) — structured so it can be swapped for a trained scikit-learn model later without touching views/templates.
- **Frontend**: Django HTML templates + Tailwind CSS (via CDN) + Material Symbols
- **Static files**: WhiteNoise
- **Database**: SQLite locally, Postgres in production (see Deployment Notes)

---

## ⚙️ Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/app-checker.git
   cd app-checker
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **(Optional) Seed sample data:**
   ```bash
   python seed_samples.py
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

7. **(Optional) Run the end-to-end smoke test:**
   ```bash
   python test_flow.py
   ```

---

## 📁 Project Structure

```text
├── appcheck/                  # Core Django application
│   ├── migrations/            # Database schema migrations
│   ├── ml/                    # Prediction engine (predictor.py)
│   ├── templates/appcheck/    # HTML UI templates (home, check_app, result, past_checks, base)
│   ├── models.py              # AppCheckRecord database model
│   ├── views.py               # View controllers & scan handlers
│   ├── urls.py                # App routing
│   └── admin.py                # Django admin registration
├── appcheck_project/          # Django project settings & configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/
│   └── index.py               # Vercel serverless entrypoint (wraps the Django WSGI app)
├── manage.py                  # Django CLI runner
├── seed_samples.py            # Sample app data populator
├── test_flow.py               # End-to-end verification script
├── requirements.txt           # Python package dependencies
├── vercel.json                # Vercel build/route configuration
├── .env.example                # Documented environment variables
├── .gitignore                 # Files excluded from git tracking
└── README.md                  # Project documentation
```

---

## ☁️ Deploying

### 1. Push to GitHub

```bash
cd app-checker
git init
git add .
git commit -m "Initial commit: AppCheck Django app"
git branch -M main
git remote add origin https://github.com/<your-username>/app-checker.git
git push -u origin main
```

`db.sqlite3` is intentionally excluded via `.gitignore` — don't commit a database file.

### 2. Deploy to Vercel

Import the GitHub repo at [vercel.com/new](https://vercel.com/new) (or run `vercel` from the project root with the Vercel CLI). Vercel will detect `vercel.json` and build `api/index.py` with the `@vercel/python` runtime.

**Before your first deploy, set these Environment Variables in the Vercel project settings:**

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | A long random string (`python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_ALLOWED_HOSTS` | `your-project.vercel.app` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` |
| `DATABASE_URL` | See **important note** below |

#### ⚠️ Important: SQLite will NOT work on Vercel

Vercel Functions run on a **read-only, ephemeral filesystem** — any writes to `db.sqlite3` (e.g. new app checks) will vanish, and may not even be visible between two requests hitting different function instances. This is a hosting-platform limitation, not a bug in this app.

To store real data in production, set `DATABASE_URL` to a hosted Postgres database, e.g.:
- [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (built into Vercel's dashboard)
- [Neon](https://neon.tech) or [Supabase](https://supabase.com) (generous free tiers)

Once `DATABASE_URL` is set, run migrations against it before/after your first deploy:
```bash
DATABASE_URL="postgres://..." python manage.py migrate
```

If you only want to demo the UI without persistence, you can skip `DATABASE_URL` and the app will fall back to a fresh SQLite file per invocation — checks simply won't be saved reliably between requests.

#### Static files

The UI uses Tailwind CSS and Google Fonts via CDN, so no build step is required for the app pages themselves. The Django admin's own CSS/JS is served via WhiteNoise; run `python manage.py collectstatic --noinput` and commit the generated `staticfiles/` directory if you want a styled `/admin/` in production.

---

## 🧠 How scoring works

`appcheck/ml/predictor.py` starts every app at a neutral score of 50/100 and adjusts it based on transparent signals: developer verification, privacy policy presence, rating, review volume, app age, download count, permission count/sensitivity, explicitly flagged suspicious words, and keyword scanning of sample reviews. Each adjustment is paired with a human-readable reason shown on the result page. A score ≥ 55 is classified **Genuine**; below that, **Suspicious**. Risk level follows the same score (≥80 Low, 55-79 Moderate, <55 High).
