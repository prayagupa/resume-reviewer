from app.models.review import ParsedResume, ScoreBreakdown


class ScoringEngine:
    """Weighted rubric scoring (max 100)."""

    def score(self, parsed: ParsedResume) -> tuple[int, ScoreBreakdown, list[str]]:
        breakdown = ScoreBreakdown(
            structure=self._structure_score(parsed),
            experience=self._experience_score(parsed),
            skills=self._skills_score(parsed),
            impact=self._impact_score(parsed),
            clarity=self._clarity_score(parsed),
        )
        total = min(100, breakdown.total)
        rationale = self._build_rationale(parsed, breakdown)
        return total, breakdown, rationale

    def _structure_score(self, parsed: ParsedResume) -> int:
        score = 0
        if parsed.email or parsed.phone:
            score += 6
        if parsed.has_experience_section:
            score += 5
        if parsed.has_education_section:
            score += 4
        if parsed.has_skills_section:
            score += 3
        if 500 <= len(parsed.raw_text) <= 9000:
            score += 2
        return min(20, score)

    def _experience_score(self, parsed: ParsedResume) -> int:
        score = 0
        years = parsed.years_experience
        if years >= 8:
            score += 12
        elif years >= 4:
            score += 9
        elif years >= 1:
            score += 6
        elif parsed.has_experience_section:
            score += 3

        score += min(8, parsed.progression_keyword_count * 3)
        if parsed.sections.experience_titles:
            score += 5
        return min(25, score)

    def _skills_score(self, parsed: ParsedResume) -> int:
        count = len(parsed.sections.skills)
        if count >= 8:
            return 20
        if count >= 5:
            return 16
        if count >= 3:
            return 12
        if count >= 1:
            return 8
        if parsed.has_skills_section:
            return 5
        return 0

    def _impact_score(self, parsed: ParsedResume) -> int:
        score = min(12, parsed.action_verb_count * 2)
        score += min(8, parsed.metric_count * 4)
        return min(20, score)

    def _clarity_score(self, parsed: ParsedResume) -> int:
        lines = [ln for ln in parsed.raw_text.splitlines() if ln.strip()]
        if not lines:
            return 0

        bullet_like = sum(1 for ln in lines if ln.strip().startswith(("-", "•", "*")))
        bullet_ratio = bullet_like / len(lines)

        caps_words = sum(1 for word in parsed.raw_text.split() if word.isupper() and len(word) > 2)
        caps_ratio = caps_words / max(1, len(parsed.raw_text.split()))

        score = 8
        if bullet_ratio >= 0.15:
            score += 4
        if caps_ratio < 0.08:
            score += 3
        return min(15, score)

    def _build_rationale(self, parsed: ParsedResume, breakdown: ScoreBreakdown) -> list[str]:
        points: list[str] = []

        if breakdown.structure >= 14:
            points.append("Resume includes clear contact info and standard sections.")
        elif breakdown.structure >= 8:
            points.append("Basic structure detected; some sections could be clearer.")
        else:
            points.append("Limited structure detected (missing contact or key sections).")

        if breakdown.experience >= 18:
            points.append(
                f"Strong experience signals (~{parsed.years_experience:.0f} years inferred)."
            )
        elif breakdown.experience >= 10:
            points.append("Moderate experience depth with identifiable roles.")
        else:
            points.append("Experience section is thin or hard to parse.")

        if breakdown.skills >= 14:
            points.append(f"Good skills coverage ({len(parsed.sections.skills)} recognized skills).")
        elif breakdown.skills >= 8:
            points.append("Skills section present but could include more relevant keywords.")
        else:
            points.append("Few recognized skills detected from the dictionary.")

        if breakdown.impact >= 14:
            points.append("Strong use of action verbs and quantified outcomes.")
        elif breakdown.impact >= 8:
            points.append("Some impact language found; add more metrics where possible.")
        else:
            points.append("Limited impact language (verbs and measurable results).")

        if breakdown.clarity >= 10:
            points.append("Readable formatting with reasonable clarity.")
        else:
            points.append("Formatting may reduce skim-readability for recruiters.")

        return points[:5]
