"""Continuous multi-tonal coordinate calculation and smooth distance penalties.

Replaces brittle binary flags with a continuous coordinate T in [-1.0, +1.0] and smooth
exponential penalty decay curves. Pure, deterministic, and self-balancing for multi-tonal works.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from math import exp
from typing import Final

from anime_catalogue.tags import Tag
from anime_catalogue.taxonomy import Genre, Theme

type TokenKey = tuple[type[Genre | Theme | Tag], Genre | Theme | Tag]


@dataclass(frozen=True, slots=True)
class TonalValence:
    """Valence weight in [-1.0, +1.0] for an individual taxonomy token."""

    token: Genre | Theme | Tag
    valence: float
    weight: float = 1.0


# Curated token valences mapping aesthetic, threat, and comedic poles to [-1.0, +1.0]
_TONAL_VALENCES: Final[tuple[TonalValence, ...]] = (
    # --- Bleak / Visceral Horror / Nihilism (-1.0 to -0.7) ---
    TonalValence(Theme.GORE, -1.0, 1.8),
    TonalValence(Tag.BODY_HORROR, -0.95, 1.8),
    TonalValence(Tag.BLEAK, -0.90, 1.6),
    TonalValence(Tag.DARK, -0.80, 1.5),
    TonalValence(Tag.SERIAL_KILLER, -0.85, 1.4),
    TonalValence(Genre.HORROR, -0.80, 1.5),
    TonalValence(Tag.TRAGEDY, -0.75, 1.3),
    TonalValence(Tag.DEATH_GAME, -0.75, 1.4),
    TonalValence(Tag.DEATHMATCH, -0.75, 1.4),
    TonalValence(Tag.BATTLE_ROYALE, -0.70, 1.3),
    TonalValence(Theme.SURVIVAL, -0.70, 1.3),
    TonalValence(Tag.APOCALYPSE, -0.70, 1.2),
    TonalValence(Tag.POST_APOCALYPTIC, -0.65, 1.1),
    TonalValence(Tag.TRAUMA, -0.65, 1.3),
    # --- Grounded Serious / Noir / Suspense / Psychological (-0.65 to -0.25) ---
    TonalValence(Theme.PSYCHOLOGICAL, -0.60, 1.4),
    TonalValence(Tag.GRIEF, -0.60, 1.2),
    TonalValence(Tag.BULLYING, -0.55, 1.2),
    TonalValence(Genre.SUSPENSE, -0.55, 1.3),
    TonalValence(Theme.ORGANIZED_CRIME, -0.50, 1.2),
    TonalValence(Tag.NOIR, -0.50, 1.2),
    TonalValence(Theme.HIGH_STAKES_GAME, -0.45, 1.1),
    TonalValence(Tag.MELANCHOLIC, -0.45, 1.1),
    TonalValence(Genre.DRAMA, -0.35, 1.0),
    TonalValence(Theme.MILITARY, -0.30, 0.9),
    # --- Bittersweet / Melodrama / Mild Melancholy (-0.25 to 0.0) ---
    TonalValence(Tag.BITTERSWEET, -0.20, 1.0),
    TonalValence(Tag.NOSTALGIC, -0.10, 0.8),
    # --- Warm / Uplifting / High-Spirited (+0.25 to +0.65) ---
    TonalValence(Tag.HEARTWARMING, +0.50, 1.2),
    TonalValence(Tag.COMMUNITY_LIFE, +0.50, 1.1),
    TonalValence(Tag.FOUND_FAMILY, +0.45, 1.1),
    TonalValence(Genre.SLICE_OF_LIFE, +0.45, 1.1),
    TonalValence(Genre.SPORTS, +0.35, 0.9),
    TonalValence(Theme.TEAM_SPORTS, +0.40, 1.0),
    TonalValence(Tag.SLOW_LIFE, +0.55, 1.2),
    TonalValence(Theme.CHILDCARE, +0.50, 1.1),
    TonalValence(Theme.CGDCT, +0.60, 1.3),
    # --- Pure Slapstick Gag / Absurdist / Stress-Free Iyashikei (+0.65 to +1.0) ---
    TonalValence(Theme.IYASHIKEI, +0.70, 1.5),
    TonalValence(Theme.PARODY, +0.75, 1.3),
    TonalValence(Tag.SATIRE, +0.75, 1.2),
    TonalValence(Tag.ABSURDIST, +0.85, 1.5),
    TonalValence(Theme.GAG_HUMOR, +0.90, 1.8),
    TonalValence(Genre.COMEDY, +0.50, 1.0),
)

TOKEN_VALENCE_LOOKUP: Final[dict[TokenKey, tuple[float, float]]] = {
    (type(tonal_valence.token), tonal_valence.token): (tonal_valence.valence, tonal_valence.weight)
    for tonal_valence in _TONAL_VALENCES
}

# Fatal distance threshold: Above this distance between anchor and candidate,
# retrieval candidate qualification drops the candidate immediately.
FATAL_TONAL_DISTANCE_THRESHOLD: Final[float] = 1.35

TONAL_PENALTY_GAMMA: Final[float] = 1.80


def compute_tonal_coordinate(tokens: Iterable[Genre | Theme | Tag]) -> float:
    """Compute continuous tonal coordinate T in [-1.0, +1.0].

    Self-balances multi-tonal titles:
      - Steins;Gate (Suspense/Drama + Comedy/Banter) -> ~ -0.35
      - Higurashi (Pure Horror/Gore) -> ~ -0.85
      - Nichijou (Gag Humor/Absurdist) -> ~ +0.85
    """
    total_weighted_valence = 0.0
    total_weight = 0.0
    for token in tokens:
        entry = TOKEN_VALENCE_LOOKUP.get((type(token), token))
        if entry is not None:
            valence, weight = entry
            total_weighted_valence += valence * weight
            total_weight += weight

    if total_weight == 0.0:
        return 0.0

    coordinate = total_weighted_valence / total_weight
    return max(-1.0, min(1.0, coordinate))


def is_fatal_tonal_contradiction(tone_a: float, tone_b: float) -> bool:
    """Return True if distance between anchor tone and candidate tone violates retrieval boundary."""
    return abs(tone_a - tone_b) >= FATAL_TONAL_DISTANCE_THRESHOLD


def compute_tonal_scoring_multiplier(tone_anchor: float, tone_candidate: float) -> float:
    """Compute smooth exponential scoring penalty for candidate based on tonal distance.

    Returns multiplier in (0.0, 1.0].
      - Delta T = 0.0 -> 1.0
      - Delta T = 0.4 -> ~0.75
      - Delta T = 0.8 -> ~0.31
      - Delta T = 1.2 -> ~0.07
    """
    delta = abs(tone_anchor - tone_candidate)
    return float(exp(-TONAL_PENALTY_GAMMA * (delta**2)))
