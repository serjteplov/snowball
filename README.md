# snowball

A Python project bootstrapped with modern tooling.

## Development

Create a virtual environment and install dependencies:

```bash
make setup
```

Or, if you already have a virtual environment:

```bash
make install-dev
```

Run all checks:

```bash
make check
```

This runs formatting, linting, type checking, and tests.

## Commands

- `make format` — run ruff formatter
- `make lint` — run ruff linter
- `make typecheck` — run mypy
- `make test` — run pytest
- `make check` — run all of the above
