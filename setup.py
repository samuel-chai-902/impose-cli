from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

DESCRIPTION = 'Create a CLI tool easily.'

# Setting up
setup(
    name="impose-cli",
    version='0.1.41rc1',
    author="scdev",
    author_email="samuel.chai.development@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements,
    extra_requires={
        "api": ["fastapi", "uvicorn"]
    },
    keywords=['python', 'cli', 'click'],
)