"""Default feature configuration values."""

DEFAULT_YEAR_BOUNDARIES = (1917, 1980, 1992, 2008, 2016, 2021, 2025)
DEFAULT_EPISODE_BOUNDARIES = (1, 12, 17, 29, 51, 101, 301, 500, 1000)
DEFAULT_DURATION_BOUNDARIES = (0, 6, 12, 21, 31, 46, 61, 91)
DEFAULT_SCORE_BOUNDARIES = (0, 5, 7, 9)
DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'
DEFAULT_EMBEDDING_BATCH_SIZE = 128

EMBEDDING_MODEL_CALIBRATIONS: dict[str, tuple[float, float]] = {
    'sentence-transformers/all-mpnet-base-v2': (0.42, 0.54),
    'sentence-transformers/all-MiniLM-L6-v2': (0.30, 0.375),
    'BAAI/bge-base-en-v1.5': (0.6534, 0.7179),
    'Qwen/Qwen3-Embedding-0.6B': (0.56, 0.68),
}

EMBEDDING_MODEL_BATCH_SIZES: dict[str, int] = {
    'sentence-transformers/all-mpnet-base-v2': 8,
    'sentence-transformers/all-MiniLM-L6-v2': 128,
}


def default_embedding_gate(model_identifier: str | None = None) -> tuple[float, float]:
    """Return calibrated (tau_min, tau_max) embedding soft-gate thresholds for a given model."""
    if not model_identifier:
        return EMBEDDING_MODEL_CALIBRATIONS[DEFAULT_EMBEDDING_MODEL]
    if model_identifier in EMBEDDING_MODEL_CALIBRATIONS:
        return EMBEDDING_MODEL_CALIBRATIONS[model_identifier]
    ident_lower = model_identifier.lower()
    if 'mpnet' in ident_lower:
        return EMBEDDING_MODEL_CALIBRATIONS['sentence-transformers/all-mpnet-base-v2']
    if 'minilm' in ident_lower:
        return EMBEDDING_MODEL_CALIBRATIONS['sentence-transformers/all-MiniLM-L6-v2']
    if 'bge' in ident_lower:
        return EMBEDDING_MODEL_CALIBRATIONS['BAAI/bge-base-en-v1.5']
    if 'qwen' in ident_lower:
        return EMBEDDING_MODEL_CALIBRATIONS['Qwen/Qwen3-Embedding-0.6B']
    return EMBEDDING_MODEL_CALIBRATIONS[DEFAULT_EMBEDDING_MODEL]


def default_embedding_batch_size(model_identifier: str | None = None) -> int:
    """Return the memory-calibrated embedding batch size for a model."""
    if not model_identifier:
        return EMBEDDING_MODEL_BATCH_SIZES.get(DEFAULT_EMBEDDING_MODEL, DEFAULT_EMBEDDING_BATCH_SIZE)
    if model_identifier in EMBEDDING_MODEL_BATCH_SIZES:
        return EMBEDDING_MODEL_BATCH_SIZES[model_identifier]
    ident_lower = model_identifier.lower()
    if 'mpnet' in ident_lower:
        return EMBEDDING_MODEL_BATCH_SIZES['sentence-transformers/all-mpnet-base-v2']
    if 'minilm' in ident_lower:
        return EMBEDDING_MODEL_BATCH_SIZES['sentence-transformers/all-MiniLM-L6-v2']
    return DEFAULT_EMBEDDING_BATCH_SIZE
