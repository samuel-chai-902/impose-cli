from setuptools import setup, find_packages

setup(
    name='impose-cli',
    version='0.1.0',
    description='A simple package that creates a CLI tool using just a few decorators.',
    author='Samuel Chai',
    author_email='samuel.chai.development@gmail.com',
    packages=find_packages(),
    install_requires=[line.strip() for line in open('requirements.txt', 'r').readlines()]
)