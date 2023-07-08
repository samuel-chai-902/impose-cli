import impose_cli
from impose_cli.decorators import impose


@impose_cli.decorators.impose
def _settings():
    print(2)


@impose
def print_1(z: str):
    print(z)


@impose_cli.decorators.impose
def print_2(z: str):
    print(z)