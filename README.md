<div align="center" id="logo">
  <img src="logo.png" alt="Kelbrum Logo" />
</div>

<div align="center" id="badges">
  <a href="https://vikiru.github.io/kelbrum/">
    <img src="https://img.shields.io/badge/documentation-docs-orange" alt="Documentation" />
  </a>
  <a href="https://github.com/vikiru/kelbrum/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-aqua" alt="MIT License Badge" />
  </a>
  <a href="https://github.com/vikiru/kelbrum/actions/workflows/lint.yml">
    <img src="https://github.com/vikiru/kelbrum/actions/workflows/lint.yml/badge.svg" alt="Lint workflow status" />
  </a>
  <br />
  <a href="https://github.com/vikiru/kelbrum/releases">
    <img src="https://img.shields.io/github/v/release/vikiru/kelbrum" alt="Release" />
  </a>
  <a href="https://github.com/vikiru/kelbrum/issues?q=is%3Aissue+is%3Aclosed">
    <img src="https://img.shields.io/github/issues-closed/vikiru/kelbrum" alt="Closed Issues" />
  </a>
  <a href="https://github.com/vikiru/kelbrum/pulls?q=is%3Apr+is%3Aclosed">
    <img src="https://img.shields.io/github/issues-pr-closed/vikiru/kelbrum?label=closed%20prs" alt="Closed PRs" />
  </a>
</div>

---

**Kelbrum** is an anime recommendation system web application with the sole goal of recommending anime to users based on similarity.

Catalogue metadata is fetched from the [Tenrai API](https://tenrai.org/) using [msgspec](https://github.com/jcrist/msgspec) schemas with checkpointed pagination, normalized into canonical records, and supplemented with version-controlled manual overrides for missing metadata (such as missing relationships and themes) and tags that add another layer of narrative similarity. The relationship engine models these records into a deterministic graph that clusters same-story families (collapsing sequels, prequels, and summaries) while preserving remakes, franchise spin-offs, and side stories.

Feature engineering constructs aligned numeric, categorical, and semantic text representations for each anime entry in the catalogue, using [MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for synopsis embeddings. Recommendations are generated through multi-path retrieval across feature similarity, taxonomy alignment, graph connections, and semantic embeddings. Candidates from each retrieval path are merged into a single pool, filtered for content rating compatibility, scored across matching attributes, and ranked into a deduplicated recommendation list with similarity score breakdowns.

All catalogue entries, search indexes, and recommendation batches are precomputed into static JSON artifacts with cryptographic checksums and loaded directly by the frontend. The original v1 release relied on k-means clustering with a custom weighted Manhattan and Dice similarity function; version 2 replaces this with multi-path retrieval and a relationship-aware recommendation engine.

> [!IMPORTANT]
>
> The catalogue and metadata within this project are made possible by the following sources:
>
> 1. [Tenrai API](https://tenrai.org/): Primary catalogue and relation source for v2.
> 2. [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset): Catalogue source used by v1.
> 3. [Jikan API](https://github.com/jikan-me/jikan-rest): API used by v1 to retrieve information from [MyAnimeList](https://myanimelist.net/).
>
> All external anime images, synopsis texts, and trademarks belong to their respective creators, studios, and copyright holders.

## 📖 Table of Contents

- [📖 Table of Contents](#-table-of-contents)
- [🌟 Features](#-features)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [📝 Prerequisites](#-prerequisites)
- [⚡ Setup Instructions](#-setup-instructions)
- [📜 Available Scripts](#-available-scripts)
- [✨ Acknowledgments](#-acknowledgments)
- [©️ License](#️-license)

## 🌟 Features

- **Recommendations**: Generates up to 100 recommendations for each anime, avoiding redundant same-story entries, preserving distinct franchise exploration, and remaining demographic-aware - see the [recommender package](./src/packages/recommender).
- **Top 100**: Browse the highest-rated anime across the catalogue with same-story entries collapsed to representative titles (using the maximum score across TV, movie, and ONA formats) - see the [top-100 page](./src/frontend/src/pages/top).
- **Search and Filtering**: Search anime by original, English, and Japanese titles with [FlexSearch](https://github.com/nextapps-de/flexsearch), with filtering by media type, content rating, demographic, genres, themes, score range, release year, and episode count - see the [search feature](./src/frontend/src/features/search).
- **Manual Corrections**: An iteratively growing collection of version-controlled manual overrides and corrections addressing missing metadata such as relationships, themes, and genres - see the [curation resources](./src/packages/pipeline/src/pipeline/curation.py).
- **Tags**: Introduces a dedicated tag property to enrich recommendation quality by capturing defining characteristics and nuances that cannot be represented by existing genres or themes alone - see the [features package](./src/packages/features).
- **Relationship Graph**: Graph-driven model that connects anime entries by relationship edges, applies manual corrections, distinguishes same-story families from broader franchise universes, and enables graph-aware retrieval - see the [graph package](./src/packages/graph).
- **Adaptability**: Modular, extensible architecture designed to accommodate additional media formats in the future (e.g. manga, manhwa, and manhua) alongside anime.

## 📁 Project Structure

```text
kelbrum/
└── src/
    ├── frontend/                       # TanStack Start / React static application
    │   └── src/
    │       ├── data/                   # Generated static artifacts, full entries, and search index
    │       ├── entities/               # Domain entity models, schemas, and UI components
    │       ├── features/               # Search, recommendation, and filtering feature implementations
    │       ├── pages/                  # Page-level surfaces (Home, Top Ranked, Anime Details, Recommendations)
    │       ├── routes/                 # TanStack Router type-safe file routes
    │       └── shared/                 # Shared UI primitives, shadcn components, hooks, and API helpers
    │
    └── packages/                       # Python data & recommendation workspace (uv)
        ├── catalogue/                  # Immutable indexed catalogue views & Polars query helpers
        ├── config/                     # Path resolution, environment settings, and deterministic identities
        ├── export/                     # Frontend artifact generation, projection validation, and checksums
        ├── features/                   # Feature engineering, tag vocabulary, and Polars assembly plans
        ├── fetch/                      # Tenrai API client, checkpointing, and source data acquisition
        ├── graph/                      # Relationship graph traversal, story-family & franchise policy
        ├── normalization/              # Data normalization, missingness handling, and fitted scalers
        ├── pipeline/                   # Pipeline orchestration, curation snapshot, and composition root
        ├── processing/                 # Raw snapshot cleaning, canonicalization, and taxonomy corrections
        ├── recommender/                # Multi-strategy retrieval, scoring, qualification, and ranking
        ├── storage/                    # Domain-agnostic persistence (JSON, Parquet, arrays, atomic writes)
        └── tests/                      # Python package test suite
```

## 🛠️ Tech Stack

- **Frontend**: [TypeScript](https://www.typescriptlang.org/), [React](https://react.dev/), [TanStack Start](https://tanstack.com/start), [TanStack Router](https://tanstack.com/router), [TanStack Query](https://tanstack.com/query), [Vite](https://vite.dev/), [Tailwind CSS](https://tailwindcss.com/), [Base UI](https://base-ui.com/), [shadcn/ui](https://ui.shadcn.com/), [FlexSearch](https://github.com/nextapps-de/flexsearch), [Zod](https://zod.dev/), [Lucide React](https://lucide.dev/), [React Icons](https://react-icons.github.io/react-icons/).

- **Data & Recommendation Pipeline**: [Python](https://www.python.org/), [Polars](https://pola.rs/), [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), [scikit-learn](https://scikit-learn.org/), [Sentence Transformers](https://www.sbert.net/), [MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), [msgspec](https://github.com/jcrist/msgspec), [Niquests](https://niquests.readthedocs.io/), [Loguru](https://loguru.readthedocs.io/).

- **Documentation**: [Astro](https://astro.build/), [Starlight](https://starlight.astro.build/), [GitHub Pages](https://pages.github.com/).

- **Development & Code Quality**: [pnpm](https://pnpm.io/), [uv](https://docs.astral.sh/uv/), [poethepoet](https://poethepoet.natn.io/index.html), [Oxlint](https://oxc.rs/docs/guide/usage/linter), [Oxfmt](https://oxc.rs/docs/guide/usage/formatter.html), [Ruff](https://docs.astral.sh/ruff/), [Pyrefly](https://pyrefly.org/), [ty](https://docs.astral.sh/ty/), [Knip](https://github.com/webpro-nl/knip), [Lefthook](https://github.com/evilmartians/lefthook), [Commitlint](https://commitlint.js.org/), [semantic-release](https://github.com/semantic-release/semantic-release).

- **AI Tools**: Spec-driven development using [OpenSpec](https://openspec.dev/) (since v2).

## 📝 Prerequisites

Ensure that the following prerequisites are installed on your system by following the [Setup Instructions](#-setup-instructions):

- [Node.js](https://nodejs.org/) `>= 22.12`
- [pnpm](https://pnpm.io/) `>= 11.20`
- [Python](https://www.python.org/) `>= 3.13`
- [uv](https://docs.astral.sh/uv/)

## ⚡ Setup Instructions

1. Clone this repository to your local machine:

```bash
git clone https://github.com/vikiru/kelbrum.git
cd kelbrum
```

2. Install repository and frontend dependencies:

```bash
pnpm install
```

3. Set up the Python workspace and install dependencies:

```bash
uv --directory src/packages sync --all-packages --dev
```

4. Download the [MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) Sentence Transformer model:

```bash
uv --directory src/packages run poe download-minilm
```

The model weights will be downloaded from Hugging Face and cached locally within `src/packages/data/models/huggingface/`.

5. Run the data acquisition and pipeline stages:

- Fetch catalogue entries from the Tenrai API:

```bash
uv --directory src/packages run poe fetch-entries
```

The fetched catalogue snapshots and checkpoint files are stored in `src/packages/data/source/tenrai/snapshots/` (`tenrai-anime-<profile>.json`, `tenrai-anime-<profile>.checkpoint.json`).

- Execute the end-to-end data processing, graph construction, and export pipeline:

```bash
uv --directory src/packages run poe run-pipeline
```

Derived parquet datasets and precomputed synopsis embeddings are saved to `src/packages/data/pipeline/` and `src/packages/data/embeddings/synopsis/`, while final client-ready artifacts are exported directly into `src/frontend/src/data/`.

Please check the `src/packages/logs/` directory if errors occur or if you need to inspect network requests. Specifically:
- `error.log`: Detailed failure traces and exceptions.
- `http.log`: Outbound HTTP request logs and rate-limiting diagnostics.
- `info.log`: Standard pipeline stage and execution milestones.
- `debug.log`: Verbose diagnostic output across all pipeline modules.

6. Start the frontend development server:

```bash
pnpm start
```

The application will be running and available at:

```text
http://localhost:3000
```

## 📜 Available Scripts

### Frontend & Workspace Scripts

1. Start the frontend development server:

```bash
pnpm start
```

2. Build the search index and frontend production bundle:

```bash
pnpm build
```

3. Preview the frontend production build locally:

```bash
pnpm preview
```

4. Lint frontend code using [Oxlint](https://oxc.rs/docs/guide/usage/linter):

```bash
pnpm lint
```

5. Run type-aware linting on frontend files:

```bash
pnpm lint:typecheck
```

6. Run TypeScript type checks without emitting files:

```bash
pnpm typecheck
```

7. Format files across the repository using [Oxfmt](https://oxc.rs/docs/guide/usage/formatter.html):

```bash
pnpm format
```

8. Detect unused files, exports, and dependencies with [Knip](https://github.com/webpro-nl/knip):

```bash
pnpm unused
```

### Python Data & Pipeline Scripts

1. Fetch catalogue snapshot from the Tenrai API (default profile):

```bash
uv --directory src/packages run poe fetch-entries
```

2. Fetch catalogue entries with a specific profile:

```bash
uv --directory src/packages run poe fetch-entries --mode sfw
uv --directory src/packages run poe fetch-entries --mode r-plus
uv --directory src/packages run poe fetch-entries --mode all
```

3. Run the full data and recommendation pipeline (default `r-plus` profile):

```bash
uv --directory src/packages run poe run-pipeline
```

4. Run the pipeline with a specific profile:

```bash
uv --directory src/packages run poe run-pipeline --profile sfw
uv --directory src/packages run poe run-pipeline --profile r-plus
uv --directory src/packages run poe run-pipeline --profile all
```

5. Run the Python automated test suite:

```bash
uv --directory src/packages run poe test
```

6. Format Python packages using [Ruff](https://docs.astral.sh/ruff/):

```bash
uv --directory src/packages run ruff format .
```

7. Lint Python packages using [Ruff](https://docs.astral.sh/ruff/):

```bash
uv --directory src/packages run ruff check .
```

8. Run Python strict type checking with [Pyrefly](https://pyrefly.org/) and [ty](https://docs.astral.sh/ty/):

```bash
uv --directory src/packages run pyrefly check
uv --directory src/packages run ty check
```

## ✨ Acknowledgments

- [Tenrai API](https://tenrai.org/)
- [Polars documentation](https://docs.pola.rs/)
- [scikit-learn documentation](https://scikit-learn.org/stable/)
- [Sentence Transformers documentation](https://sbert.net/)
- [GitHub Shields](https://github.com/badges/shields)

Additionally, this project would not be possible without the following sources of information:

- [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset)
- [Jikan API](https://github.com/jikan-me/jikan-rest)
- [MyAnimeList](https://myanimelist.net/)

The documentation site is built using [Starlight](https://starlight.astro.build/) by [Astro](https://astro.build/) and hosted via [GitHub Pages](https://pages.github.com/).

All external images and text used within this application belong to their respective owners and sources.

## ©️ License

The contents of this repository are licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

[MIT](LICENSE) &copy; 2024-present Visakan Kirubakaran.
