# Task 1 - Hello World App Engine App

Minimal Flask app for Google App Engine Standard Environment with Python 3, based on the official Google Cloud App Engine Python quickstart.

Deployed URL:

```text
https://task1-dot-gen-lang-client-0038539374.uc.r.appspot.com
```

## Files

- `main.py` - Flask app and request log.
- `app.yaml` - App Engine Standard configuration.
- `templates/index.html` - Hello World page.
- `static/` - small CSS and browser console log.
- `tests/test_main.py` - route test.

## Run locally

```powershell
cd Task1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python main.py
```

Open `http://localhost:8080`.

## Run tests

```powershell
cd Task1
python -m pytest
```

## Deploy

From the `Task1` folder:

```powershell
gcloud auth login
gcloud config set project YOUR_APP_ID
gcloud app deploy
gcloud app browse
```

The deployed URL for newer App Engine apps is usually:

```text
https://YOUR_APP_ID.REGION_ID.r.appspot.com
```

For older App Engine apps it can also be:

```text
http://YOUR_APP_ID.appspot.com
```
