# Changelog

All notable changes to `negspacy` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] — 2026-04-20

### Added
- `src/` package layout (`src/negspacy/`); prevents accidental imports of the in-development package during testing.
- PEP 561 `py.typed` marker so downstream users pick up the library's type hints.
- Top-level `tests/` directory with shared session-scoped `nlp` fixture in `conftest.py`; `test.py` split into `test_negation.py` and `test_termsets.py`.
- GitHub Actions workflows: `ci.yml` (lint + test matrix across ubuntu/macos/windows × Python 3.10–3.13 + build) and `release.yml` (tag-triggered PyPI publish via OIDC trusted publishing).
- Test coverage for previously uncovered paths: `chunk_prefix`, `ent_types` filtering, `extension_name` override, `span_keys` edge cases, termset `add_patterns`/`remove_patterns` round-trips and `ValueError` paths, `en_clinical_sensitive` and `es_clinical` termsets.
- `scispacy`-dependent tests are now gated behind `pytest.importorskip("scispacy")` and skip cleanly when the optional model is not installed.
- This `CHANGELOG.md`.

### Changed
- Packaging consolidated into a single `pyproject.toml` (PEP 621) using `hatchling` as the build backend. Version now lives in `src/negspacy/__init__.py` and is read dynamically by hatch.
- Runtime dependency bumped to `spacy>=3.8,<4.0`.
- Minimum Python bumped to `>=3.10` (spaCy 3.8 transitively requires `thinc>=8.3.12`, which dropped Python 3.9).
- `PhraseMatcher.add(key, None, *patterns)` calls migrated to the modern `add(key, patterns)` signature, silencing spaCy 3.8 deprecation warnings.
- Type hints updated to py310 builtins (`list[str]`, `X | None`).
- Linting and formatting migrated from Black/isort/flake8 to `ruff` + `ruff-format`; `.pre-commit-config.yaml` refreshed.
- CI migrated from Azure Pipelines to GitHub Actions.
- `CONTRIBUTING.md` rewritten for the new development workflow and now documents the release process.
- README build badge updated to point at the GitHub Actions workflow.

### Removed
- `setup.py`, `setup.cfg`, `requirements.txt`, and the tracked `negspacy.egg-info/` directory.
- `azure-pipelines.yml`.
- Support for Python 3.6 / 3.7 / 3.8 / 3.9.
- Dead `test_issue7` test (had no assertions).

### Fixed
- Extracted the `process_span` closure in `negation.py` into an explicit `_apply_negation` method, fixing a latent loop-variable-capture issue (ruff B023) flagged by the updated linter.

## [1.0.3] — 2022-05-25

### Fixed
- Code clean-up and speed improvements to the matcher pipeline.

## [1.0.2] — 2022-01-20

### Added
- Spanish clinical termset (`es_clinical`), contributed by @j6e ([#51]).
- Apply negex to `doc.spans` via the new `span_keys` config ([#57]).

### Changed
- Simplified span-group arguments — removed `use_spans` in favour of `span_keys`.

## [1.0.1] — 2021-10-25

### Fixed
- Corrected the `psuedo_negations` → `pseudo_negations` key typo across built-in termsets.

## [1.0.0] — 2021-02-22

### Changed
- **BREAKING:** rewritten for spaCy 3.0's new pipeline-component interface. The component is now registered via `@Language.factory("negex", ...)` and added with `nlp.add_pipe("negex", config={...})`. Direct `Negex(nlp, ...)` construction is no longer the public entry point. Not backwards-compatible with pre-1.0 users — pin `negspacy==0.1.9` if you still need spaCy 2.x support.
- Termset management moved into a dedicated `termset` class exposing `get_patterns()`, `add_patterns()`, and `remove_patterns()`.

## [0.1.9] — 2020-11-18

### Added
- `extension_name` config so multiple `Negex` instances can coexist in a single pipeline with distinct extension attributes.
- `add_patterns` / `remove_patterns` helpers for modifying built-in termsets at runtime.

### Changed
- Default termset switched from `en` to `en_clinical`.

---

[Unreleased]: https://github.com/jenojp/negspacy/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/jenojp/negspacy/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/jenojp/negspacy/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/jenojp/negspacy/compare/1.0.1...v1.0.2
[1.0.1]: https://github.com/jenojp/negspacy/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/jenojp/negspacy/compare/v0.1.9...1.0.0
[0.1.9]: https://github.com/jenojp/negspacy/releases/tag/v0.1.9

[#51]: https://github.com/jenojp/negspacy/pull/51
[#57]: https://github.com/jenojp/negspacy/pull/57
