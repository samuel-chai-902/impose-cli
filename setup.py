from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

DESCRIPTION = 'Create a CLI tool easily.'

# Setting up
setup(
    name="impose-cli",
    version='0.3.5',
    author="scdev",
    author_email="samuel.chai.development@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements,
    keywords=['python', 'cli', 'click'],
)