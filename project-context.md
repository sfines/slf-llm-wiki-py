# Project Context and Standards

## Coding Standards
*   **Logging**: Use `structlog` for structured logging. Do not build custom logging solutions.
*   **Tooling**: Use `uv` for package management, `nox` for test automation, `pytest` for testing, `ruff` for linting/formatting, and `mypy` for type checking.
*   **Python Version**: The project targets Python 3.14 exclusively.
*   **Configuration**: `ruff` and `mypy` configuration must be maintained within `pyproject.toml`.
*   **Execution**: `ruff` and `mypy` must be executable via `nox` sessions. All tests MUST run via `nox` and `uv`. `nox` MUST be configured to use the `uv` backend.