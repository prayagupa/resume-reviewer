# Resume Reviewer

A web app that uploads a PDF resume, extracts its text, and returns a structured summary plus a **pickup score** (0–100) estimating how likely a hiring manager is to shortlist it.

The MVP uses a **local, rule-based analyzer** (no cloud LLM). A future version can plug in an LLM via Ollama or an API. See [docs/design-spec.md](docs/design-spec.md) for the full design.

## What it does

1. Accept a text-based PDF resume (max 5 MB, 10 pages).
2. Extract text with [pdfplumber](https://github.com/jsvine/pdfplumber).
3. Parse sections (experience, education, skills) and detect signals (contact info, action verbs, metrics).
4. Score the resume with a transparent weighted rubric.
5. Return a summary, score band, and rationale bullets.

**Score bands**

| Score | Band |
|-------|------|
| 0–39 | Low likelihood |
| 40–69 | Moderate likelihood |
| 70–100 | Strong likelihood |

## Tech stack

- Python 3.14+
- [FastAPI](https://fastapi.tiangolo.com/) + Jinja2 (HTML UI)
- pdfplumber, Pydantic

The active application lives in [`python/`](python/). The repo root still contains a legacy Scala/Spring scaffold that is not used by the resume reviewer.

## Run locally

### Prerequisites

- Python 3.14+ (`python3.14 --version`)

### Setup

```bash
cd python
python3.14 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Optional: copy environment defaults and adjust if needed.

```bash
cp .env.example .env
```

### Start the server

From the `python/` directory with the virtualenv activated:

```bash
uvicorn app.main:app --reload --port 8000
```

### Use the app

| What | URL / command |
|------|----------------|
| Upload UI | http://127.0.0.1:8000/review |
| Health check | http://127.0.0.1:8000/health |
| API docs | http://127.0.0.1:8000/docs |

**API example** — upload a PDF and get JSON:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/reviews \
  -F "resume=@/path/to/resume.pdf"
```

### Run tests

```bash
cd python
source .venv/bin/activate
pytest tests/ -v
```

## Project layout

```
python/
├── app/              # FastAPI app, extraction, analysis, services
├── templates/        # Jinja2 HTML pages
├── static/           # CSS
├── data/             # Skills dictionary for scoring
└── tests/            # pytest suite
docs/
├── design-spec.md    # Software design spec
└── thoughts.md       # Product notes
```

## Configuration

Environment variables (see `python/.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `RESUME_MAX_FILE_SIZE_BYTES` | `5242880` | Max upload size (5 MB) |
| `RESUME_MAX_PAGES` | `10` | Max PDF pages |
| `ANALYZER` | `rule` | Analyzer mode (`rule` for MVP) |
| `SHOW_EXTRACTED_TEXT` | `false` | Show text preview on results page |

## Disclaimer

Scores and summaries are automated estimates for feedback only — not hiring decisions.
