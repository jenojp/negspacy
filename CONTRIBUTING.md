# Contributing

Thanks for your interest in negspacy!

## Reporting issues

Please open a GitHub issue for any bugs, feature requests, or questions.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
pre-commit install
```

[uv](https://github.com/astral-sh/uv) is also supported and faster:

```bash
uv venv && uv pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=negspacy --cov-report=term-missing
```

## Linting and formatting

[ruff](https://docs.astral.sh/ruff/) handles linting and formatting (replacing Black, isort, and flake8).

```bash
# check
ruff check .
# auto-fix
ruff check --fix .
# format
ruff format .
```

pre-commit runs ruff automatically on every commit. To run manually across all files:

```bash
pre-commit run --all-files
```

## Pull requests

- Fork the repo and open a PR against `master`.
- Keep PRs small and focused — one concern per PR.
- All tests must pass before review.
- Do not push directly to `master`.

## Releasing

Releases are fully automated. A pushed tag matching `v*` triggers `.github/workflows/release.yml`, which builds the sdist and wheel and uploads them to PyPI via [OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/). No API tokens, no local `twine upload`.

### Cutting a new release

1. **Bump the version.** Edit `src/negspacy/__init__.py` and update `__version__`. This is the single source of truth — `pyproject.toml` reads it dynamically via `[tool.hatch.version]`.
2. **Update `CHANGELOG.md`.** Move items from the `[Unreleased]` section into a new `[X.Y.Z] — YYYY-MM-DD` section and update the compare links at the bottom of the file. Leave an empty `[Unreleased]` stub above the new section.
3. **Open a release PR** titled `release: vX.Y.Z` against `master`. CI must pass.
4. **Merge the release PR** after maintainer review.
5. **Tag the merge commit** from `master`:
   ```bash
   git checkout master && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
6. **Watch the `release` workflow run** on GitHub Actions. On success, the new version is on PyPI within a minute.

Do not publish to PyPI from a local machine, and do not commit API tokens.

### One-time trusted-publisher setup (already configured)

For reference — this has already been done for `negspacy` on PyPI and does not need to be repeated:

- A trusted publisher is registered on the PyPI project page (PyPI → Your projects → `negspacy` → Publishing) binding the `jenojp/negspacy` repository, the workflow file `release.yml`, and the GitHub environment `pypi`.
- A GitHub environment named `pypi` exists in the repository settings. `release.yml` references it via `environment: pypi`, which is what allows the OIDC token exchange to succeed.

If the project is ever transferred to a new account or the workflow filename changes, the trusted-publisher registration must be updated on PyPI to match — otherwise the publish step will fail with an authentication error.
