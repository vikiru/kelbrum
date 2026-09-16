"""Derived identities for processing artifacts."""

from collections.abc import Collection, Mapping, Sequence

from config import derive_payload_identity, derive_stage_identity
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.eligibility import EligibilityPolicy
from processing.theme_corrections import theme_correction_registry_identity

PROCESSING_PRODUCER_IDENTITY = 'processing.build_canonical'


def processing_artifact_identity(
    *,
    source_sha256: str,
    policy: EligibilityPolicy,
    theme_additions: Mapping[int, Sequence[str]],
    theme_removals: Mapping[int, Sequence[str]] | None = None,
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
        registry_identity=curation_identity
        or derive_payload_identity(
            {
                'theme_additions': sorted((anime_id, tuple(themes)) for anime_id, themes in theme_additions.items()),
                'theme_removals': sorted(
                    (anime_id, tuple(themes)) for anime_id, themes in (theme_removals or {}).items()
                ),
                'theme_corrections_identity': theme_correction_registry_identity(),
                'tagged_anime_ids': sorted(tagged_anime_ids),
            }
        ),
        producer_identity=PROCESSING_PRODUCER_IDENTITY,
    )
