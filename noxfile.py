import contextlib
from tempfile import NamedTemporaryFile
from typing import Generator, IO

import nox
from nox.sessions import Session

nox.options.sessions = "tests", "mypy", "lint", "safety"
LOCATIONS = "src", "tests", "noxfile.py"
PYTHONS = ["3.8"]


@nox.session(python=PYTHONS)
def tests(session: Session) -> None:
    args = session.posargs or ["--cov", "-m", "not e2e"]
    if not session._runner.global_config.reuse_existing_virtualenvs:
        session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", "tests", *args)


@nox.session(python=PYTHONS)
def mypy(session: Session) -> None:
    args = session.posargs or LOCATIONS
    _install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=PYTHONS)
def lint(session: Session) -> None:
    args = session.posargs or LOCATIONS
    _install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
    )
    session.run("flake8", *args)


@nox.session(python=PYTHONS)
def safety(session: Session) -> None:
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
    args = session.posargs or LOCATIONS
    _install_with_constraints(session, "black")
    session.run("black", *args)


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
            "--format=requirements.txt",
            f"--output={requirements.name}",
            *args,
            external=True,
        )
        yield requirements
