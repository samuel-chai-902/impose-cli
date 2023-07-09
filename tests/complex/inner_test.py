import impose_cli
from impose_cli.decorators import impose


@impose
def _settings():
    print(2)


def print_1(z: str = "yes"):
    """
    Print1 prints the z parameter.
    :param z: A simple string.
    :return:
    """
    print(z)


def print_2(z: str):
    print(z)