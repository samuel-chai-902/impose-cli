import pytest
from impose_cli.impose_cli import impose, impose_cli


@impose
def function_without_arguments():
    return True


@impose
def function_with_arguments(arg1, arg2):
    return True


@impose
def function_with_arguments_with_defaults(arg1: str = 'yes'):
    return arg1


def testing_correct_argument_parsing():
    commands = impose_cli(execute=False).commands
    assert len(commands['function-without-arguments'].params) == 0
    assert len(commands['function-with-arguments'].params) == 2
    assert commands['function-with-arguments'].params[0].opts == ['arg1']
    assert commands['function-with-arguments'].params[0].type.name == 'text'
    assert len(commands['function-with-arguments-with-defaults'].params) == 1
    assert commands['function-with-arguments-with-defaults'].params[0].required == False
    assert commands['function-with-arguments-with-defaults'].params[0].default == 'yes'
    assert commands['function-with-arguments-with-defaults'].params[0].opts == ['--arg1']


def testing_impose_decorator():
    assert function_without_arguments() == True
    assert function_with_arguments(None, None) == True
    assert function_with_arguments_with_defaults('str') == 'str'