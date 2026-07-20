# Task 2 - App Engine Datastore Database

Simple HTTP database app for Google App Engine Standard Environment with Python 3 and Firestore in Datastore mode.

The root page has a small browser UI for running the same commands.

Deployed URL after deployment:

```text
https://gen-lang-client-0038539374.uc.r.appspot.com
```

Assignment-style URL:

```text
http://gen-lang-client-0038539374.appspot.com
```

## Commands

```text
/set?name={variable_name}&value={variable_value}
/get?name={variable_name}
/unset?name={variable_name}
/numequalto?value={variable_value}
/undo
/redo
/end
```

All responses are plain text. Invalid or missing query parameters return an `ERROR:` message with status `400`.

## Run locally

```powershell
cd Task2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python main.py
```

Open `http://localhost:8080`.

For local route tests, no Google credentials are needed because tests use an in-memory storage adapter.

## Run tests

```powershell
cd Task2
python -m pytest
```

## Deploy

Enable Datastore API if needed:

```powershell
gcloud services enable datastore.googleapis.com --project=YOUR_APP_ID
```

Deploy from this folder:

```powershell
gcloud app deploy app.yaml --project=YOUR_APP_ID
```

## Implementation Notes

- Variables are stored by key in Datastore.
- Counts are stored by value so `/numequalto` can fetch one entity.
- SET and UNSET commands write operation entities for undo/redo.
- Undo and redo stack heads are stored in one state entity.
- `/end` deletes all Task 2 entity kinds.
