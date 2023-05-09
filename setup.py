import subprocess
from setuptools import setup, find_packages


def get_version():
    try:
        version = subprocess.check_output(['git', 'describe', '--tags']).decode().strip()
    except subprocess.CalledProcessError:
        version = '0.0.1'
    return version


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

VERSION = get_version()
DESCRIPTION = 'Create a CLI tool easily.'

# Setting up
setup(
    name="impose-cli",
    version=VERSION,
    author="scdev",
    author_email="samuel.chai.development@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements,
    keywords=['python', 'cli', 'click'],
)