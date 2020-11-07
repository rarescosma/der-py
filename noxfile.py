import nox


nox.options.sessions = "lint", "tests"
LOCATIONS = "src", "tests", "noxfile.py"
PYTHONS = ["3.8"]


@nox.session(python=PYTHONS)
def tests(session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    if not session._runner.global_config.reuse_existing_virtualenvs:
        session.run("poetry", "install", external=True)
    session.run("pytest", "tests", *args)


@nox.session(python=PYTHONS)
def lint(session):
    args = session.posargs or LOCATIONS
    session.install("flake8", "flake8-black", "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=PYTHONS)
def black(session):
    args = session.posargs or ("--quiet", *LOCATIONS)
    session.install("black")
    session.run("black", *args)
