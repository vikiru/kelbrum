import os
import subprocess
import sys

import pytest

from config import IdentityInputs, derive_identity, derive_payload_identity, derive_stage_identity


def test_identity_is_deterministic_for_equal_inputs() -> None:
    inputs = IdentityInputs(
        contract_identity='canonical-v1',
        source_identity='snapshot-sha256',
        ordered_ids=(3, 1, 2),
        configuration_identity='features-a',
        policy_identity='rating-b',
        registry_identity='tags-c',
        producer_identity='producer-d',
    )

    assert derive_identity(inputs) == derive_identity(inputs)


def test_identity_changes_when_a_semantic_input_changes() -> None:
    base = IdentityInputs(contract_identity='canonical-v1', source_identity='snapshot-sha256')

    assert derive_identity(base) != derive_identity(base.__replace__(policy_identity='rating-v2'))


def test_payload_identity_is_independent_of_mapping_insertion_order() -> None:
    first = {'policy': {'rating': 'G', 'age': 13}, 'paths': ('genre', 'theme')}
    second = {'paths': ('genre', 'theme'), 'policy': {'age': 13, 'rating': 'G'}}

    assert derive_payload_identity(first) == derive_payload_identity(second)


def test_payload_identity_is_stable_for_unordered_containers_across_processes() -> None:
    code = (
        'from config import derive_payload_identity; '
        "print(derive_payload_identity({'values': frozenset({'alpha', 'beta', 'gamma'})}))"
    )
    outputs = []
    for hash_seed in ('1', '2'):
        environment = {**os.environ, 'PYTHONHASHSEED': hash_seed}
        # The executable and code are fixed test constants; no external input is executed.
        result = subprocess.run(  # noqa: S603
            [sys.executable, '-c', code],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        outputs.append(result.stdout.strip())

    assert outputs[0] == outputs[1]


def test_stage_identity_includes_all_cache_reuse_inputs() -> None:
    def stage_identity(*, registry_identity: str = 'registry-a') -> str:
        return derive_stage_identity(
            'features',
            contract_identity='feature-v1',
            source_identity='snapshot-sha256',
            ordered_ids=(3, 1, 2),
            configuration_identity='config-a',
            policy_identity='policy-a',
            registry_identity=registry_identity,
            producer_identity='producer-d',
        )

    assert stage_identity() == stage_identity()
    assert stage_identity(registry_identity='registry-b') != stage_identity()


def test_stage_identity_rejects_an_empty_stage() -> None:
    with pytest.raises(ValueError, match='non-empty'):
        derive_stage_identity('', contract_identity='v1', source_identity='source')
