from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_review_form_page() -> None:
    response = client.get("/review")
    assert response.status_code == 200
    assert "Resume Reviewer" in response.text


def test_api_create_review(sample_pdf_bytes: bytes) -> None:
    response = client.post(
        "/api/v1/reviews",
        files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 100
    assert data["band"]
    assert data["summary"]
    assert len(data["rationale"]) >= 3
    assert "Python" in data["sections"]["skills"]
    assert data["analyzer_used"] == "rule"


def test_feature_flags_endpoint() -> None:
    response = client.get("/api/v1/feature-flags")
    assert response.status_code == 200
    data = response.json()
    assert "effective" in data
    assert data["ui_enabled"] is True


def test_feature_flags_update_sets_cookies() -> None:
    response = client.post(
        "/api/v1/feature-flags",
        json={"llm_analyzer": True, "show_extracted_text": True},
    )
    assert response.status_code == 200
    assert response.cookies.get("ff_llm") == "1"
    assert response.cookies.get("ff_show_text") == "1"


def test_api_rejects_non_pdf() -> None:
    response = client.post(
        "/api/v1/reviews",
        files={"resume": ("resume.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_html_review_submit(sample_pdf_bytes: bytes) -> None:
    response = client.post(
        "/review",
        files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    assert "Pickup score" in response.text
    assert "Summary" in response.text
