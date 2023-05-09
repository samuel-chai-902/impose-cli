from subprocess import run
from os import environ
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

DESCRIPTION = 'Create a CLI tool easily.'

# Setting up
setup(
    name="impose-cli",
    version=environ['BRANCH_TAG'],
    author="scdev",
    author_email="samuel.chai.development@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements,
    keywords=['python', 'cli', 'click'],
)