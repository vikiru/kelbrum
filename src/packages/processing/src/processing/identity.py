"""Derived identities for processing artifacts."""

from collections.abc import Collection, Mapping, Sequence

from config import derive_payload_identity, derive_stage_identity
from features.origin_language_overrides import (
    ORIGIN_LANGUAGE_OVERRIDES_VERSION,
    get_manual_origin_languages,
    manual_origin_language_csv_hash,
)
from features.tag_assignment import tag_assignment_registry_identity
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.eligibility import EligibilityPolicy
from processing.excluded_ids import EXCLUDED_IDS
from processing.metadata_corrections import theme_correction_registry_identity

PROCESSING_PRODUCER_IDENTITY = 'processing.build_canonical'


def processing_artifact_identity(
    *,
    source_sha256: str,
    policy: EligibilityPolicy,
    theme_additions: Mapping[int, Sequence[str]],
    theme_removals: Mapping[int, Sequence[str]] | None = None,
    genre_additions: Mapping[int, Sequence[str]] | None = None,
    tagged_anime_ids: Collection[int],
    policy_identity: str,
    curation_identity: str | None = None,
) -> str:
    """Derive the identity shared by processing writes and cache reuse checks."""
    return derive_stage_identity(
        'processing',
        contract_identity=PROCESSING_AUDIT_SCHEMA_VERSION,
        source_identity=source_sha256,
        configuration_identity=derive_payload_identity(policy),
        policy_identity=policy_identity,
        registry_identity=derive_payload_identity(
            {
                'curation_identity': curation_identity
                or derive_payload_identity(
                    {
                        'theme_additions': sorted(
                            (anime_id, tuple(themes)) for anime_id, themes in theme_additions.items()
                        ),
                        'theme_removals': sorted(
                            (anime_id, tuple(themes)) for anime_id, themes in (theme_removals or {}).items()
                        ),
                        'genre_additions': sorted(
                            (anime_id, tuple(genres)) for anime_id, genres in (genre_additions or {}).items()
                        ),
                        'theme_corrections_identity': theme_correction_registry_identity(),
                        'tag_assignments': tag_assignment_registry_identity(),
                        'origin_languages': (
                            ORIGIN_LANGUAGE_OVERRIDES_VERSION,
                            sorted(
                                (anime_id, language.value)
                                for anime_id, language in get_manual_origin_languages().items()
                            ),
                            manual_origin_language_csv_hash(),
                        ),
                        'tagged_anime_ids': sorted(tagged_anime_ids),
                    }
                ),
                'excluded_ids': sorted(EXCLUDED_IDS),
            }
        ),
        producer_identity=PROCESSING_PRODUCER_IDENTITY,
    )
