from features.cache import configuration_hash
from graph.registry import manual_relationships_identity
from processing.eligibility import EligibilityPolicy
from processing.identity import processing_artifact_identity


def test_curated_registry_changes_are_scoped_to_their_consuming_stage() -> None:
    def artifact_identity(theme: str) -> str:
        return processing_artifact_identity(
            source_sha256='source-a',
            policy=EligibilityPolicy(),
            theme_additions={10: (theme,)},
            tagged_anime_ids=(),
            policy_identity='eligibility-v2',
        )

    assert artifact_identity('Theme') != artifact_identity('Other Theme')
    assert manual_relationships_identity({1: (2,)}) != manual_relationships_identity({1: (3,)})
    assert configuration_hash({}, tag_assignment_identity='assignments-a') != configuration_hash(
        {}, tag_assignment_identity='assignments-b'
    )
