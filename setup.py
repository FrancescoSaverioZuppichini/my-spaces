from setuptools import find_packages, setup

setup(
    name="my-spaces",
    version="0.0.1",
    packages=find_packages(include=["src", "src.*"]),
    install_requires=["jinja2", "typer[all]", "docker"],
    entry_points={
        "console_scripts": ["my-spaces=src.main:main"],
    },
)
