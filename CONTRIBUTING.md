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
