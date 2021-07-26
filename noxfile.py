"""Nox sessions."""
import contextlib
from tempfile import NamedTemporaryFile
from typing import Generator, IO

import nox
from nox.sessions import Session

nox.options.sessions = "tests", "mypy", "lint", "safety"
LOCATIONS = "src", "tests", "noxfile.py", "docs/conf.py"
PYTHONS = ["3.9"]


@nox.session(python=PYTHONS)
def tests(session: Session) -> None:
    """Run the test suite using pytest."""
    m_args = ["-m", "not e2e"] if "-m" not in session.posargs else []
    cov_args = ["--cov"]
    args = [*m_args, *cov_args, *(session.posargs or [])]
    _install_package(session)
    _install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "requests-mock"
    )
    session.run("pytest", "tests", *args)


@nox.session(python=PYTHONS)
def coverage(session: Session) -> None:
    """Upload coverage data."""
    _install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python=PYTHONS)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or LOCATIONS
    _install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=PYTHONS)
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or LOCATIONS
    _install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
    )
    session.run("flake8", *args)


@nox.session(python=PYTHONS)
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    _install_with_constraints(session, "safety")
    with _requirements_file(session, "--without-hashes") as requirements:
        session.run(
            "safety",
            "check",
            f"--file={requirements.name}",
            "--full-report",
        )


@nox.session(python=PYTHONS)
def black(session: Session) -> None:
    """Run the black code formatter."""
    args = session.posargs or LOCATIONS
    _install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=PYTHONS)
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or []
    _install_package(session)
    _install_with_constraints(session, "pytest", "xdoctest")
    session.run("pytest", "src/der_py", "--xdoc", *args)


@nox.session(python=PYTHONS)
def docs(session: Session) -> None:
    """Build the documentation."""
    _install_package(session)
    _install_with_constraints(session, "sphinx", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "docs", "docs/_build")


def _install_package(session: Session) -> None:
    if not session._runner.global_config.reuse_existing_virtualenvs:
        session.run("poetry", "install", "--no-dev", external=True)


def _install_with_constraints(session: Session, *args: str) -> None:
    with _requirements_file(session) as requirements:
        session.install(f"--constraint={requirements.name}", *args)


@contextlib.contextmanager
def _requirements_file(
    session: Session, *args: str
) -> Generator[IO[bytes], None, None]:
    with NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            *args,
            external=True,
        )
        yield requirements
