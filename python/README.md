# Resume Reviewer (Python)

PDF resume upload, text extraction, rule-based scoring, and summary.

## Requirements

- Python 3.14+

## Setup

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/review

API: `POST /api/v1/reviews` with multipart field `resume` (PDF).

## Test

```bash
pytest tests/ -v
```
