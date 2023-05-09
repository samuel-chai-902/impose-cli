from setuptools import setup, find_packages

VERSION = '0.0.15'
DESCRIPTION = 'Create a CLI tool easily.'

# Setting up
setup(
    name="impose-cli",
    version=VERSION,
    author="scdev",
    author_email="samuel.chai.development@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['click'],
    keywords=['python', 'cli', 'click'],
)