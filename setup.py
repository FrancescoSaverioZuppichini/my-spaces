from setuptools import find_packages, setup

setup(
    name="my-spaces",
    description="Self Host Hugging Face Spaces",
    version="0.0.1",
    packages=find_packages(include=["my_spaces", "my_spaces.*"]),
    include_package_data=True,
    install_requires=["jinja2", "typer[all]", "docker"],
    entry_points={
        "console_scripts": ["my-spaces=my_spaces.main:main"],
    },
)
