import re
from pathlib import Path

from app.models.review import ParsedResume, ResumeSections

SECTION_HEADERS = {
    "experience": re.compile(r"^(work\s+)?experience|employment|professional\s+experience$", re.I),
    "education": re.compile(r"^education|academic(\s+background)?$", re.I),
    "skills": re.compile(r"^(technical\s+)?skills|core\s+competencies|technologies$", re.I),
    "summary": re.compile(r"^(professional\s+)?summary|profile|objective$", re.I),
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.I)

DATE_RANGE_RE = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?"
    r"(\d{4})\s*[-–—to]+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?"
    r"(\d{4}|Present|Current)",
    re.I,
)
YEAR_ONLY_RE = re.compile(r"\b(?:19|20)\d{2}\b")

ACTION_VERBS = {
    "built", "led", "managed", "developed", "designed", "implemented", "improved",
    "increased", "reduced", "delivered", "launched", "optimized", "created",
    "automated", "scaled", "mentored", "architected", "deployed",
}

PROGRESSION_KEYWORDS = {"lead", "senior", "staff", "principal", "manager", "director", "head"}

METRIC_RE = re.compile(r"(\d+%|\$\s?\d+|\d+k\b|\d+\s?(?:users|customers|requests|ms|x))", re.I)

TITLE_LINE_RE = re.compile(
    r"^(senior\s+|staff\s+|lead\s+)?"
    r"(software|backend|frontend|full[\s-]?stack|data|devops|platform|ml|machine learning)\s+"
    r"(engineer|developer|architect|scientist|analyst)",
    re.I,
)


def load_skill_dictionary(path: Path) -> set[str]:
    if not path.exists():
        return set()
    skills: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        skill = line.strip()
        if skill:
            skills.add(skill.lower())
    return skills


class ResumeParser:
    def __init__(self, skills_path: Path) -> None:
        self._skill_dict = load_skill_dictionary(skills_path)

    def parse(self, text: str) -> ParsedResume:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lowered = text.lower()

        email_match = EMAIL_RE.search(text)
        phone_match = PHONE_RE.search(text)
        linkedin_match = LINKEDIN_RE.search(text)

        sections = self._split_sections(lines)
        skills = self._extract_skills(text, sections.get("skills", []))
        education = self._extract_bullets(sections.get("education", []))
        experience_titles = self._extract_experience_titles(
            sections.get("experience", []),
            lines,
        )

        years = self._estimate_years_experience(text)
        page_estimate = max(1, min(10, len(text) // 2500 + 1))

        action_verb_count = sum(1 for verb in ACTION_VERBS if re.search(rf"\b{verb}\b", lowered))
        metric_count = len(METRIC_RE.findall(text))
        progression_count = sum(1 for kw in PROGRESSION_KEYWORDS if re.search(rf"\b{kw}\b", lowered))

        name = self._guess_name(lines)

        return ParsedResume(
            raw_text=text,
            name=name,
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0) if phone_match else None,
            linkedin=linkedin_match.group(0) if linkedin_match else None,
            years_experience=years,
            sections=ResumeSections(
                skills=skills,
                education=education[:5],
                experience_titles=experience_titles[:5],
            ),
            has_experience_section=bool(sections.get("experience")),
            has_education_section=bool(sections.get("education")),
            has_skills_section=bool(sections.get("skills")),
            page_count_estimate=page_estimate,
            action_verb_count=action_verb_count,
            metric_count=metric_count,
            progression_keyword_count=progression_count,
        )

    def _split_sections(self, lines: list[str]) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current: str | None = None

        for line in lines:
            header_key = self._match_section_header(line)
            if header_key:
                current = header_key
                sections.setdefault(current, [])
                continue
            if current:
                sections[current].append(line)

        return sections

    def _match_section_header(self, line: str) -> str | None:
        cleaned = line.strip().rstrip(":")
        for key, pattern in SECTION_HEADERS.items():
            if pattern.match(cleaned):
                return key
        return None

    def _extract_skills(self, text: str, skill_lines: list[str]) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()

        candidates = " ".join(skill_lines) if skill_lines else text
        tokens = re.split(r"[,;|•\n]", candidates)
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            lower = token.lower()
            if lower in self._skill_dict and lower not in seen:
                seen.add(lower)
                found.append(token if token[0].isupper() else token.title())

        if not found:
            for skill in sorted(self._skill_dict):
                if re.search(rf"\b{re.escape(skill)}\b", text.lower()):
                    display = skill.title() if skill.islower() else skill
                    if display.lower() not in seen:
                        seen.add(display.lower())
                        found.append(display)

        return found[:15]

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets: list[str] = []
        for line in lines:
            cleaned = re.sub(r"^[-•*]\s*", "", line).strip()
            if len(cleaned) > 8:
                bullets.append(cleaned)
        return bullets

    def _extract_experience_titles(self, experience_lines: list[str], fallback_lines: list[str]) -> list[str]:
        titles: list[str] = []
        for line in experience_lines or fallback_lines:
            if TITLE_LINE_RE.search(line) and line not in titles:
                titles.append(line)
        return titles

    def _estimate_years_experience(self, text: str) -> float:
        years: list[int] = []
        current_year = 2026

        for match in DATE_RANGE_RE.finditer(text):
            start_year = int(match.group(1))
            end_token = match.group(2)
            end_year = current_year if end_token.lower() in {"present", "current"} else int(end_token)
            if end_year >= start_year:
                years.append(end_year - start_year)

        if years:
            return float(min(40, max(years)))

        year_hits = [int(y) for y in YEAR_ONLY_RE.findall(text)]
        if len(year_hits) >= 2:
            span = max(year_hits) - min(year_hits)
            return float(min(40, max(0, span)))

        return 0.0

    def _guess_name(self, lines: list[str]) -> str | None:
        for line in lines[:5]:
            if EMAIL_RE.search(line) or PHONE_RE.search(line):
                continue
            if any(p.match(line.rstrip(":")) for p in SECTION_HEADERS.values()):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isalpha() for w in words if w):
                return line
        return None
