from impose_cli.decorators import impose


@impose
def print_2(x: int):
    print(x)