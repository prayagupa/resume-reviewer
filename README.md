# Resume Reviewer

A web app that uploads a PDF resume, extracts its text, and returns a structured summary plus a **pickup score** (0–100) estimating how likely a hiring manager is to shortlist it.

The default analyzer is **local and rule-based** (no cloud LLM). **Phase 3** adds an optional **Ollama LLM** path behind a feature flag, with automatic fallback to rules if the LLM is unavailable. See [docs/design-spec.md](docs/design-spec.md) for the full design.

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

From the **repository root** (not `python/`):

```bash
python3.14 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Optional: copy environment defaults and adjust if needed.

```bash
cp .env.example .env
```

### Start the server

With the virtualenv activated from the repository root:

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
  -F "resume=@/path/to/resume.pdf" \
  -F "job_title=Senior Software Engineer" \
  -F "required_skills=Python,AWS"
```

### Feature flags (Phase 3)

LLM analysis is **off by default** (`FEATURE_LLM_ANALYZER=false`). To test:

1. Start [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.2`
2. Open http://127.0.0.1:8000/review — use the **Feature flags** panel to enable **LLM analyzer**, then **Save flags** or submit a review.
3. Or set `FEATURE_LLM_ANALYZER=true` in `.env` to enable globally.

| Variable | Default | Description |
|----------|---------|-------------|
| `FEATURE_LLM_ANALYZER` | `false` | Allow LLM analyzer (env master switch) |
| `FEATURE_FLAG_UI_ENABLED` | `true` | Show dev flag toggles on upload page |
| `LLM_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `LLM_MODEL` | `llama3.2` | Model name |

API flag overrides: `X-Feature-LLM: true` header or `POST /api/v1/feature-flags` JSON body.

### Docker

```bash
docker build -t resume-reviewer .
docker run -p 8000:8000 resume-reviewer
```

### Run tests

```bash
source .venv/bin/activate
pytest -v
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

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `RESUME_MAX_FILE_SIZE_BYTES` | `5242880` | Max upload size (5 MB) |
| `RESUME_MAX_PAGES` | `10` | Max PDF pages |
| `SHOW_EXTRACTED_TEXT` | `false` | Show full extracted text on results page |
| `FEATURE_LLM_ANALYZER` | `false` | Enable LLM analyzer by default |
| `FEATURE_FLAG_UI_ENABLED` | `true` | Dev UI for toggling flags |

## Disclaimer

Scores and summaries are automated estimates for feedback only — not hiring decisions.
