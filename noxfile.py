import nox

# Configure nox to use uv as the default venv backend
nox.options.default_venv_backend = "uv"


@nox.session(python=["3.14"])
def tests(session):
    """Run tests with pytest."""
    session.install("-e", ".", "pytest", "pytest-asyncio", "pytest-mock")
    session.run("pytest", *session.posargs)


@nox.session
def lint(session):
    """Run linting with ruff."""
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def typecheck(session):
    """Run type checking with mypy."""
    session.install("mypy")
    session.run("mypy", "src")
