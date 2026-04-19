# CLAUDE.md

Guidance for Claude Code when working on this repository. Read this in full before making any changes.

## Project purpose

`negspacy` is a spaCy v3 pipeline component that identifies negated entities and spans in text, based on the NegEx algorithm (Chapman et al., 2001). It is published to PyPI as `negspacy` and is widely used in clinical NLP and biomedical research.

The package is small, pure-Python, and has two responsibilities:
1. Provide a `negex` pipeline factory that sets a boolean `._.negex` extension on entities or spans.
2. Provide a `termset` API for built-in and user-defined negation pattern lists.

## Public API — DO NOT break without an explicit major version bump

Downstream users and research papers depend on these surfaces. Breaking any of them is a breaking change and requires coordination with the maintainer, not a silent PR.

### Factory registration
The component must remain registered as `"negex"` via `@Language.factory("negex", ...)` so that `nlp.add_pipe("negex", config={...})` continues to work.

### Default config keys
These keys, names, and default semantics must be preserved:
- `neg_termset` — dict with keys `pseudo_negations`, `preceding_negations`, `following_negations`, `termination`. Defaults to `termset("en_clinical").get_patterns()`.
- `ent_types` — optional list of entity label strings to filter on. Default `None` (all ents).
- `extension_name` — name of the boolean attribute set on ents/spans. Default `"negex"`, accessed as `ent._.negex`.
- `chunk_prefix` — optional list of strings that may appear as a chunk prefix (e.g., `["no"]`). Default `None`.
- `span_keys` — optional list of `doc.spans` keys to process instead of (or in addition to) `doc.ents`. Default `None`.

### Extension attribute
`Token`, `Span`, and/or entity objects expose a boolean attribute registered under `extension_name` (default `negex`). `ent._.negex` and `span._.negex` are the documented access patterns. Do not rename, re-type, or change the default without a major version bump.

### Termset API
`negspacy.termsets.termset(language)` must continue to accept the three built-in strings:
- `"en"` — general English
- `"en_clinical"` — default; adds clinical phrases
- `"en_clinical_sensitive"` — adds historical/irrelevance phrases

The returned object must continue to expose `get_patterns()`, `add_patterns(dict)`, and `remove_patterns(dict)` with the existing dict schema.

### Pattern category names
The four pattern keys are a public contract: `pseudo_negations`, `preceding_negations`, `following_negations`, `termination`. Note the historical misspelling `psuedo_negations` existed in pre-1.0 versions — the correct spelling `pseudo_negations` is the current one and must be preserved.

## Target repository layout (post-modernization)

The modernization effort moves the project to a standard `src/` layout with a dedicated `tests/` directory and a single `pyproject.toml` as the source of truth.

```
negspacy/                       # repo root
  src/
    negspacy/
      __init__.py
      negation.py               # Negex class + @Language.factory("negex")
      termsets.py               # termset() + built-in en / en_clinical / en_clinical_sensitive
      py.typed                  # PEP 561 marker (type hints are shipped)
  tests/
    __init__.py
    conftest.py                 # shared fixtures (spaCy model loading, etc.)
    test_negation.py            # split out from old negspacy/test.py
    test_termsets.py            # split out from old negspacy/test.py
  .github/
    workflows/
      ci.yml                    # replaces azure-pipelines.yml
      release.yml               # tag-triggered PyPI publish via OIDC
    ISSUE_TEMPLATE/
  .pre-commit-config.yaml       # ruff + standard hygiene hooks
  pyproject.toml                # single source of truth (PEP 621)
  CLAUDE.md                     # this file
  CHANGELOG.md                  # Keep a Changelog format, seeded from git history
  CONTRIBUTING.md
  README.md
  LICENSE                       # MIT
```

Files to be removed during modernization: `setup.py`, `setup.cfg`, `requirements.txt`, `azure-pipelines.yml`, and the legacy `negspacy/test.py` (contents moved into `tests/`).

Adopting the `src/` layout is deliberate: it prevents accidental imports of the in-development package during testing and forces tests to run against the installed package, which catches packaging bugs early.

## Packaging and dependencies

`pyproject.toml` is the single source of truth. Use **hatchling** as the build backend (simpler than setuptools, zero-config, official PyPA).

Runtime dependencies live in `[project.dependencies]`. Development dependencies live in `[project.optional-dependencies]` under a `dev` extra, which installs lint, test, and docs tooling together. This is the convention most Python users expect and works with `pip install -e ".[dev]"` out of the box.

Sketch:
```toml
[project]
name = "negspacy"
dynamic = ["version"]
requires-python = ">=3.9"
dependencies = [
    "spacy>=3.8,<4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-cov",
    "ruff",
    "pre-commit",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/negspacy/__init__.py"
```

Do not re-introduce `requirements.txt`. If a specific use case needs a pinned lockfile (e.g., CI reproducibility), generate it with `uv pip compile` or `pip-compile` and check in a `requirements.lock` rather than a hand-maintained file.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
pre-commit install
```

`uv` is also supported and faster if the contributor prefers it:
```bash
uv venv
uv pip install -e ".[dev]"
```

Supported matrix:
- Python: 3.9, 3.10, 3.11, 3.12, 3.13
- spaCy: `>=3.8,<4.0` (pin bump to 4.0 when spaCy v4 stabilizes)

Note: test models like `en_core_web_sm` must match the installed spaCy minor version. CI should either resolve the compatible model version automatically or pin deliberately.

## Testing

Tests live in the top-level `tests/` directory, not inside the package. Filenames follow `test_*.py`; pytest discovery is the default.

pytest is configured in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
```

Run the full suite:
```bash
pytest
```

With coverage:
```bash
pytest --cov=negspacy --cov-report=term-missing
```

Before opening any PR, Claude must:
1. Run the full test suite and confirm all tests pass.
2. If tests fail, STOP and report. Do not "fix" tests by weakening assertions or skipping them. Test fixes require explicit approval.
3. For changes that touch negation logic or termsets, add or update tests in the same PR.

Testing priorities (known under-covered areas — ask before assuming coverage):
- `span_keys` code path (SpanGroup processing)
- `chunk_prefix` behavior
- `extension_name` override (multiple Negex instances in one pipeline)
- `ent_types` filtering
- Pattern add/remove round-trips on termset objects

Shared fixtures (e.g., a loaded `en_core_web_sm` pipeline) belong in `tests/conftest.py` and should be session-scoped to avoid reloading the model per test.

## Linting and formatting

`ruff` replaces black, isort, flake8, and pyupgrade. One tool, fast, consistent. Configuration lives in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "RUF"]

[tool.ruff.format]
quote-style = "double"
```

`.pre-commit-config.yaml` runs:
- `ruff` (check + fix)
- `ruff-format`
- Standard hygiene: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`, `check-added-large-files`
- `check-merge-conflict`

Hook versions must be current at the time of modernization — do not copy stale versions from the existing `.pre-commit-config.yaml`. Always run `pre-commit autoupdate` to resolve latest.

Run locally before committing:
```bash
pre-commit run --all-files
```

Type hints are encouraged. `mypy` is optional at this stage; if added later, configure under `[tool.mypy]` in `pyproject.toml` with strict mode scoped to `src/negspacy/` only.

## Commit and PR conventions

- **Commits**: Conventional Commits style (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`, `refactor:`).
- **Branches**: `feat/<short-desc>`, `fix/<short-desc>`, `chore/<short-desc>`.
- **PRs**: small and focused — one concern per PR. PR description must include:
  - Motivation
  - What changed
  - **What did NOT change** (explicit scope fence against drive-by edits)
  - Test evidence (output or description of new tests)
  - Reviewer checklist
- **Do not merge.** The maintainer reviews and merges every PR manually.
- **Do not push directly to `master`.**

## Known upgrade constraints

This project was last released (v1.0.3) in May 2022 against spaCy 3.3. When jumping to spaCy 3.8, be aware of the following spaCy changes that may affect behavior:

- **spaCy 3.4**: typing-related internal changes; unlikely to affect us but worth a test run.
- **spaCy 3.5**: dropped Python 3.6/3.7; our supported matrix must start at 3.9.
- **spaCy 3.7**: Pydantic v2 migration in parts of the config system. If any config validation in this repo uses Pydantic directly, it may need updates.
- **spaCy 3.8**: changes to model packaging and the `--require-parent` flag. Primarily affects trained pipelines, not extensions like ours, but worth verifying test fixtures still load.

Cython is NOT used in this package. Pure Python only. Do not introduce Cython, Rust, or other compiled components.

## Things not to change without discussion

Open an issue or ask the maintainer before touching any of the following:
- Any item listed under "Public API" above.
- The built-in contents of `en`, `en_clinical`, or `en_clinical_sensitive` termsets (changing default negation phrases would silently change research results for existing users).
- The `Negex` class name or module path (`negspacy.negation.Negex`).
- The behavior of how negation is determined algorithmically (scope rules, termination handling). Bug fixes with test coverage are welcome; "improvements" to the algorithm are not unless explicitly requested.
- License (MIT). Do not add code from sources with incompatible licenses.

## PyPI and release

Published as `negspacy` on PyPI: https://pypi.org/project/negspacy/

Release flow:
1. Bump version in `src/negspacy/__init__.py` (single source via `[tool.hatch.version]`).
2. Update `CHANGELOG.md`.
3. Open a release PR. On merge, tag `vX.Y.Z` on master.
4. Tag push triggers `.github/workflows/release.yml`, which builds and publishes to PyPI via trusted publishing (OIDC, no API tokens).

Do not publish to PyPI from a local machine. Do not commit API tokens.

## References

- NegEx paper: Chapman, Bridewell, Hanbury, Cooper, Buchanan. https://doi.org/10.1006/jbin.2001.1029
- spaCy Universe listing: https://spacy.io/universe
- Related maintainer library: https://github.com/jenojp/extractacy
- Zenodo DOI for citation: see README badge

## For Claude Code specifically

- This file is committed to the repository and is public. Do not put secrets, private roadmap, or personal context here.
- For private or experimental context, use `CLAUDE.local.md` (gitignored).
- When running on Claude Code on the web, the VM setup commands should install dev dependencies and download `en_core_web_sm` before starting work.
- Always read `MODERNIZATION_PLAN.md` (once created) at the start of any modernization task to understand the current PR sequence and status.
