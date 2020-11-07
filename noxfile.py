import tempfile

import nox


nox.options.sessions = "lint", "safety", "tests"
LOCATIONS = "src", "tests", "noxfile.py"
PYTHONS = ["3.8"]


@nox.session(python=PYTHONS)
def tests(session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    if not session._runner.global_config.reuse_existing_virtualenvs:
        session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", "tests", *args)


@nox.session(python=PYTHONS)
def lint(session):
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
def black(session):
    args = session.posargs or LOCATIONS
    _install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=PYTHONS)
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        _install_with_constraints(session, "safety")
        session.run(
            "safety",
            "check",
            f"--file={requirements.name}",
            "--full-report",
        )


def _install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
