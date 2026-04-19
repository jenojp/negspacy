# Modernization Audit Report — `negspacy`

## 1. Packaging

### Current state (3 conflicting sources)
| File | Name | Version | spaCy pin | python_requires | Classifiers |
|---|---|---|---|---|---|
| `setup.py` | `negspacy` | `"v1.0.5"` (note `v` prefix) | `>=3.0.1,<4.0.0` | `>=3.6.0` | 3.6–3.11 |
| `setup.cfg` | `negspacy` | `1.0.5` | `>=3.0.2,<4.0.0` | `>=3.6` | 3.6–3.11 |
| `pyproject.toml` | — (no metadata) | — | — | — | — |
| `requirements.txt` | — | — | unpinned `spacy` | — | — |
| `negspacy.egg-info/` | build artifact — should not be in VCS | | | | |

**Authoritative?** Effectively `setup.py` wins at build time because `pyproject.toml` only declares the setuptools backend with no `[project]` table, and modern setuptools falls back to `setup.py` when `setup.cfg` is partial. But `setup.py` and `setup.cfg` disagree on the spaCy lower bound and the version string, which is a latent bug — `blocker`.

### Target `pyproject.toml` (PEP 621, hatchling)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "negspacy"
dynamic = ["version"]
description = "A spaCy pipeline component for negating concepts in text (NegEx)."
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.9"
authors = [{ name = "Jeno Pizarro", email = "jenopizzaro@gmail.com" }]
keywords = ["nlp", "spacy", "negation", "clinical"]
classifiers = [
  "Development Status :: 5 - Production/Stable",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Topic :: Scientific/Engineering",
  "Typing :: Typed",
]
dependencies = ["spacy>=3.8,<4.0"]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov", "ruff", "pre-commit"]

[project.urls]
Homepage = "https://github.com/jenojp/negspacy"
Issues   = "https://github.com/jenojp/negspacy/issues"

[tool.hatch.version]
path = "src/negspacy/__init__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/negspacy"]

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E","F","W","I","UP","B","SIM","RUF"]

[tool.ruff.format]
quote-style = "double"
```

**Findings**
- Delete `setup.py`, `setup.cfg`, `requirements.txt`, `negspacy.egg-info/` — `blocker`, PR #1.
- `src/negspacy/__init__.py` is currently empty; it must expose `__version__ = "..."` for `[tool.hatch.version]` — `blocker`, PR #1.
- Add `src/negspacy/py.typed` marker (type hints already present in `negation.py`) — `important`, PR #1.

---

## 2. CI

### Current `azure-pipelines.yml`
- Trigger: `master`, `develop`, `releases/*`.
- Matrix: Py 3.11 / 3.12 × Ubuntu 22.04 / macOS 14 / Windows 2022 (six jobs).
- Steps: upgrade pip/setuptools → `pip install -r requirements.txt` → `python -m spacy download en_core_web_sm` → `cd negspacy && pytest test.py` → `python setup.py sdist` → install sdist → re-run tests. scispacy job commented out.
- No lint, no coverage upload, no publish step, no Python 3.9/3.10/3.13.

### Proposed `.github/workflows/ci.yml`
```yaml
name: CI
on:
  push: { branches: [master, develop] }
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .

  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pip install -e ".[dev]"
      - run: python -m spacy download en_core_web_sm
      - run: pytest --cov=negspacy --cov-report=xml
      - uses: codecov/codecov-action@v5
        if: matrix.os == 'ubuntu-latest' && matrix.python == '3.12'

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }
```

### `.github/workflows/release.yml` (tag-triggered, OIDC)
```yaml
name: release
on:
  push:
    tags: ["v*"]
jobs:
  pypi:
    runs-on: ubuntu-latest
    environment: pypi           # restrict in repo settings
    permissions:
      id-token: write           # OIDC for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install build && python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

**Findings**
- Azure Pipelines must be removed; README badge will break — `important`, PR #4.
- 3.9/3.10/3.13 not tested today — `important`, PR #4.
- No lint, no coverage, no publish — `important`, PR #4/#7.
- PyPI trusted publisher must be configured in pypi.org project settings before the first release merge — `blocker` for first release, PR #7 prep.

---

## 3. Dependencies & spaCy 3.3 → 3.8 API audit

| Area | Current usage | 3.8 status |
|---|---|---|
| `@Language.factory("negex", default_config=...)` | `negation.py:17–26` | Unchanged, works |
| `Span.set_extension(name, default=False, force=True)` | `negation.py:68–69` | Unchanged |
| `PhraseMatcher.add("pseudo", None, *patterns)` | `negation.py:103, 108, 113, 116` | **Deprecated 2-arg form** (positional `on_match=None`). Works but emits `UserWarning`. Should be `self.matcher.add("pseudo", patterns)` (list) or `add("pseudo", patterns, on_match=None)`. — `important`, PR #2 |
| `doc.spans[key]` list assignment in test | `negspacy/test.py:153, 165` | 3.x-compatible (creates `SpanGroup`); span iteration unchanged |
| `from spacy.pipeline import EntityRuler` in tests | `negspacy/test.py:6, 86` | Still importable in 3.8, but `EntityRuler(nlp)` direct construction is brittle; `nlp.add_pipe("entity_ruler")` is preferred. The test `test_issue7` doesn't actually use the ruler anyway — dead test, PR #5 |
| Pydantic | Not imported by this project | No fallout |
| `typing.List/Dict/Tuple/Set/Optional` | `negation.py:5` | Valid but outdated since 3.9+; ruff UP006/UP035 will flag |
| `spacy.tokens.SpanGroup` | Not imported | n/a |

No direct pydantic use → no v1→v2 migration needed. — `nice-to-have` note, PR #2.

spaCy model: CI downloads `en_core_web_sm` without pinning. With `spacy>=3.8`, it will pull the latest `3.8.x` compatible model via `spacy download`; but if someone pins spaCy differently locally, model mismatches can surface. Safer to run `python -m spacy download en_core_web_sm` post-install and let the resolver pick — current approach is acceptable. — `nice-to-have`, PR #4.

---

## 4. Code quality

**Type hints**
- `negation.py` is partially typed (method signatures yes, but `doc`, `nlp`, `span` are untyped). Consider `Doc`/`Span` annotations — `nice-to-have`, PR #2.
- `termsets.py` has **zero** type hints and uses lowercase-class `termset` (violates PEP 8) — `important`, PR #2 (rename would break API; keep alias but add `Termset = termset`). Per CLAUDE.md "Things not to change without discussion," don't rename — leave class name as-is; just add type hints. — `nice-to-have`.

**Ruff rules likely to fire**
| Rule | Location | Fix |
|---|---|---|
| `E712` (== False/True) | `negspacy/test.py:80` (`assert doc.ents[1]._.negex == False`) | `assert not doc.ents[1]._.negex` |
| `E721` (use isinstance) | `negspacy/test.py:97` (`assert type(patterns) == dict`) | `isinstance(patterns, dict)` |
| `C408` (dict()/list() literal) | `termsets.py:5, 8, 100, 173`; `negation.py:138–140` | `{}` / `[]` |
| `UP006/UP007/UP035` (use `list[...]`, `X | None`) | `negation.py:5, 62–66, 83–86, 118, 171, 201` | py39 target allows `Optional[...]` → `X | None` |
| `F401` unused imports | `negspacy/test.py:6` (`EntityRuler`), `negspacy/test.py:1` (`pytest` is unused) | remove |
| `PT009/B011` | none significant | — |
| `SIM102/SIM117` | `negation.py:228–242` nested `if` chains | small refactor |

**Dead code / bugs**
- `negspacy/test.py:83–89` (`test_issue7`): has no assertions — dead test — `important`, PR #5.
- `negspacy/test_scispacy_dep.py:4–5`: `import negation` / `from termsets import termset` — **broken imports** (relative-style without package) — either fix or move/guard this file. Currently not run by CI (commented out). — `important` if we re-enable, `nice-to-have` otherwise, PR #6.
- `negspacy/test_scispacy_dep.py:75` (`__test_umls2`): dunder-prefix means pytest skips it; remove — `nice-to-have`, PR #6.
- `negation.py:227–243` `process_span` inner function returns `span` in happy path but `None` on early-return branches; the caller discards the value — unused return, `nice-to-have`.
- `negation.py:9`: `default_ts = termset("en_clinical").get_patterns()` runs at import time and **mutates a shared dict reference** when users later call `termset(...).add_patterns/remove_patterns` (the `termset` class stores `LANGUAGES[lang]` by reference in `self.terms`). This is a latent bug separate from modernization. Flag: `nice-to-have` (out of scope; don't fix silently per CLAUDE.md — file an issue).
- `__init__.py` is empty — hatch can't read version. Must set `__version__` — `blocker`, PR #1.

---

## 5. Tests

Current: single file `negspacy/test.py` (seven functions), plus `test_scispacy_dep.py` (not run). To be moved to `tests/` per target layout.

**Coverage gaps** (severity `important` unless noted, all PR #5):
- `chunk_prefix`: only covered in the disabled scispacy file → **zero active coverage**.
- `ent_types` filtering: documented but no assertion-bearing test.
- `extension_name` override: not tested; two `Negex` instances with different extension names in one pipeline is a documented pattern and untested.
- `span_keys`: one happy-path test (`test_spans`). Missing: multiple span keys, missing span key gracefully handled (`_safe_get_spans` is defensive but untested), span-plus-ents combined.
- Termset `add_patterns`/`remove_patterns`: counts are checked, but the actual strings are not verified to be present/absent after round-trip. Also no test for `ValueError` on an unknown key.
- Invalid `neg_termset` raises `KeyError` (`negation.py:79`) — untested.
- `en_clinical_sensitive` and `es_clinical` termsets have no tests at all.
- `termination_boundaries` sentence-splitting logic (especially interaction with `sents`) has no direct unit test.

**Fixture issues**
- `spacy.load("en_core_web_sm")` is called in every test function → slow and duplicative. Move to session-scoped fixture in `tests/conftest.py` — `important`, PR #5.
- `build_docs()` assertions depend on specific `en_core_web_sm` output; e.g. `("December 31, 2020", True)` assumes the NER model emits that exact span. Pinning the model version in CI and documenting it is necessary; otherwise a `en_core_web_sm` update can break tests for non-logic reasons — `important`, PR #5.
- No pytest config in repo today; discovery works only because tests live next to code — `blocker` once we move to `src/` layout (tests would not find the package otherwise; the `src/` layout forces installed-package imports, which is the point). PR #1 + PR #5.

---

## 6. Docs

- `README.md:7` — Azure Pipelines Build Status badge will 404 after migration. Replace with GHA badge. — `important`, PR #4.
- `README.md:20–24` — install section omits `python -m spacy download en_core_web_sm`, which every example below requires. — `nice-to-have`, PR #3.
- No version-compat table (which spaCy/Python matrix is supported). — `nice-to-have`, PR #3.
- **No `CHANGELOG.md`**. CLAUDE.md mandates "Keep a Changelog." — `blocker` before release, PR #7.
- `CONTRIBUTING.md` still tells contributors to use Black; we're moving to ruff. 4 lines of stale content, should be rewritten with the new dev-setup commands. — `important`, PR #3.
- `.pre-commit-config.yaml` pins `pre-commit-hooks` v2.3.0 (2019) and `black` v22.10.0 — stale; entire file should be replaced to call ruff + ruff-format and `pre-commit autoupdate` run. — `important`, PR #3.
- README `Negex` import example is currently `from negspacy.negation import Negex` but the README never actually *uses* the imported symbol — that's fine, but consider showing the minimal pattern without the unused import. — `nice-to-have`.

---

## 7. Open issues (#1, #2, #3)

All three are **closed**; triaged per request:

| # | Title | Status | Disposition |
|---|---|---|---|
| 1 | Install error on negspacy (pip install) | closed 2019 | **already-fixed** — Windows `UnicodeDecodeError` in `setup.py:11` reading `README.md` without encoding. `setup.py` still exists with the same defect (`io.open(..., encoding="utf8")` was added, so the original bug is fixed). Moot once `setup.py` is deleted in PR #1. |
| 2 | Set up CI with Azure Pipelines | closed PR from 2019 | **out-of-scope** — superseded; GHA migration in PR #4. |
| 3 | Update `azure-pipelines.yml` for Azure Pipelines | closed PR from 2019 | **out-of-scope** — superseded by PR #4. |

No currently open issues to reconcile.

---

## Proposed PR sequence

Each PR is small, independently reviewable, and runnable end-to-end.

1. **PR #1 — chore(packaging): move to `src/` layout + single `pyproject.toml`**
   Delete `setup.py`, `setup.cfg`, `requirements.txt`, `negspacy.egg-info/`. Move `negspacy/` → `src/negspacy/`. Populate `__init__.py` with `__version__`. Add `py.typed`. Move `negspacy/test.py` → `tests/test_negation.py` + `tests/test_termsets.py` (no logic changes; just split). Add `tests/conftest.py` with session-scoped `nlp` fixture. Verifies `pip install -e ".[dev]" && pytest` works.
   *Severity: blocker.*

2. **PR #2 — chore(deps): modernize spaCy usage for 3.8 + type hints**
   Replace `PhraseMatcher.add("x", None, *patterns)` with `add("x", patterns)` (4 call sites in `negation.py`). Update type hints to py39 generics. No behavior change; add tests around the matcher only if missing.
   *Severity: important.*

3. **PR #3 — chore(lint): ruff + pre-commit + CONTRIBUTING rewrite**
   Replace `.pre-commit-config.yaml` with ruff/ruff-format + hygiene hooks (latest via `pre-commit autoupdate`). Rewrite `CONTRIBUTING.md` for ruff and the new dev setup. Run `pre-commit run --all-files` in one sweep commit.
   *Severity: important.*

4. **PR #4 — ci: replace Azure Pipelines with GitHub Actions**
   Add `ci.yml` (lint + test matrix 3.9/3.10/3.11/3.12/3.13 × ubuntu/macos/windows + build). Delete `azure-pipelines.yml`. Swap README build-status badge. Add coverage via Codecov.
   *Severity: important.*

5. **PR #5 — test: fill coverage gaps**
   Add tests for `chunk_prefix`, `ent_types`, `extension_name` override, `span_keys` edge cases, termset `add/remove` round-trip and error paths, both English-variant termsets. Remove dead `test_issue7` (or add real assertions). Verify no regressions.
   *Severity: important.*

6. **PR #6 — test(scispacy): un-break or quarantine `test_scispacy_dep.py`**
   Either fix imports and gate behind `pytest.importorskip("scispacy")` + an optional CI job, or delete the file. Maintainer decision.
   *Severity: nice-to-have.*

7. **PR #7 — release: changelog + release workflow + PyPI trusted publisher docs**
   Seed `CHANGELOG.md` (Keep a Changelog) from git history; add `release.yml`; document the one-time PyPI trusted-publisher setup in `CONTRIBUTING.md`. Do not tag or publish in this PR.
   *Severity: blocker (before any new release), gating for all subsequent version bumps.*

**Do not merge as a single PR.** Each PR above is independently valuable and reviewable; the maintainer gates every merge.
