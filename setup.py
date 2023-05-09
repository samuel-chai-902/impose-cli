from subprocess import run
from setuptools import setup, find_packages


def get_version():
    try:
        version = run('git describe tags', capture_output=True, shell=True)
        version = ''.join(filter(str.isdigit, version))
    except Exception as e:
        print(str(e))
        version = '0.0.1'
    print(version)
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