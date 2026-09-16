"""Generate review-only tag nominations from synopsis evidence."""

from collections.abc import Sequence

import msgspec

from fetch.contracts import TenraiAnimeEntry


class SynopsisNominationRule(msgspec.Struct, frozen=True):
    """One deterministic phrase rule used to discover possible tag assignments."""

    tag_id: str
    terms: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.tag_id.strip():
            raise ValueError('synopsis nomination tag ID cannot be empty')
        if not self.terms or any(not term.strip() for term in self.terms):
            raise ValueError('synopsis nomination terms cannot be empty')


class SynopsisNomination(msgspec.Struct, frozen=True):
    """A reviewable candidate; this record never changes production curation by itself."""

    anime_id: int
    title: str
    tag_id: str
    matched_terms: tuple[str, ...]
    evidence: str


def nominate_synopsis_tags(
    entries: Sequence[TenraiAnimeEntry], rules: Sequence[SynopsisNominationRule]
) -> tuple[SynopsisNomination, ...]:
    """Return deterministic synopsis candidates for human review."""
    nominations: list[SynopsisNomination] = []
    for entry in entries:
        synopsis = (entry.synopsis or '').strip()
        if not synopsis:
            continue
        normalized_synopsis = synopsis.casefold()
        for rule in rules:
            matched_terms = tuple(term for term in rule.terms if term.casefold() in normalized_synopsis)
            if matched_terms:
                nominations.append(
                    SynopsisNomination(
                        anime_id=entry.mal_id,
                        title=entry.title,
                        tag_id=rule.tag_id,
                        matched_terms=matched_terms,
                        evidence=_evidence_excerpt(synopsis, matched_terms[0]),
                    )
                )
    return tuple(nominations)


def _evidence_excerpt(synopsis: str, term: str, window: int = 120) -> str:
    """Return a compact, human-readable excerpt around the first matched term."""
    start = synopsis.casefold().find(term.casefold())
    excerpt_start = max(0, start - window)
    excerpt_end = min(len(synopsis), start + len(term) + window)
    return synopsis[excerpt_start:excerpt_end].strip()
