from subprocess import run, CalledProcessError
from setuptools import setup, find_packages


def get_version():
    output = run('git describe --tags', capture_output=True, shell=True).stdout.decode('utf-8')
    return ''.join(filter(lambda x: x.isdigit() or x == '.', list(output)))


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