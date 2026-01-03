from setuptools import find_packages, setup

setup(
    name="cf_core",
    version="0.1.0",
    package_dir={"cf_core": "."},
    packages=["cf_core"],
    install_requires=[
        "pydantic>=2.9.2",
        "sqlalchemy>=2.0.35",
        "typer>=0.12.5",
        "structlog>=24.4.0",
        "rich>=10.0.0",
        "duckdb>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "cf=cf_core.cli.main:run_cli",
        ],
    },
)
