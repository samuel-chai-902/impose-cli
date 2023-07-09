import pytest
from impose_cli.impose_cli import impose_cli
from impose_cli.decorators import impose


@impose
def function_without_arguments():
    return True


@impose
def function_with_arguments(arg1: str, arg2: str):
    return True


@impose
def function_with_arguments_with_defaults(arg1: str = 'yes'):
    return arg1


def testing_correct_argument_parsing():
    cli = impose_cli(launch_type="cli", return_before_executing=False)
    print(1)
