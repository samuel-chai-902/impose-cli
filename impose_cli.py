import ast
import click
from importlib.util import spec_from_file_location, module_from_spec
from inspect import getframeinfo, currentframe
from inspect import Parameter, signature as sig
from os import listdir
from os.path import exists, join, dirname, abspath


def impose(func):
    return func


def impose_cli(target: str = None) -> None:
    """
    If target is a directory, then each file will be a group and all functions will be a command
    If medium is a file, then there will be no group and all functions will be a command
    :param target:
    :return:
    """

    class ImposeFunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.imposed_functions = []

        def visit_FunctionDef(self, node):
            if hasattr(node, 'decorator_list'):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'impose':
                        self.imposed_functions.append(node.name)

    def find_imposed_functions(filename):
        with open(filename, 'r') as file:
            file_contents = file.read()
        module = ast.parse(file_contents)
        visitor = ImposeFunctionVisitor()
        visitor.visit(module)
        return visitor.imposed_functions

    def find_files(origin, target):
        if target is None:
            return [origin]

        else:
            directory = join(dirname(origin), target)
            if not exists(directory):
                raise FileNotFoundError(f"There is no directory {directory}.")

            dirs = [x for x in listdir(directory) if x.endswith('.py')]
            return [abspath(join(directory, f)) for f in dirs]


    def load_module_from_file(file_path, module_name):
        spec = spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def analyze_functions(module, function):
        signature = sig(getattr(module, function))
        parameters = signature.parameters
        args_with_defaults = [(p.name, p.annotation if p.annotation.__name__ != '_empty' else None) for p in parameters.values() if p.default != Parameter.empty]
        args_without_defaults = [(p.name, p.annotation if p.annotation.__name__ != '_empty' else None) for p in parameters.values() if p.default == Parameter.empty]
        return args_without_defaults, args_with_defaults

    def create_dynamic_group(group_name, command_list):
        dynamic_group = click.Group(name=group_name)

        for cmd in command_list:
            dynamic_command = click.Command(name=cmd['name'].replace('_', '-'), callback=cmd['callback'])

            for arg in cmd['arguments']:
                arg_name = arg[0].replace('_', '-')
                if arg[1] is not None:
                    dynamic_command.params.append(click.Argument((arg_name,), type=arg[1]))
                else:
                    dynamic_command.params.append(click.Argument((arg_name,)))

            for opt in cmd['options']:
                opt_name = opt[0].replace('_', '-')
                if opt[1] is not None:
                    dynamic_command.params.append(click.Argument((f"--{opt_name}",), type=opt[1]))
                else:
                    dynamic_command.params.append(click.Option((f"--{opt_name}",)))

            dynamic_group.add_command(dynamic_command)

        return dynamic_group

    origin_files = find_files(getframeinfo(currentframe().f_back)[0], target)

    meta = {}
    for origin_file in origin_files:
        module_name = origin_file.split('/')[-1].replace('.py', '')
        meta[module_name] = []
        module = load_module_from_file(origin_file, module_name)
        functions = find_imposed_functions(origin_file)
        for function in functions:
            args, opts = analyze_functions(module, function)
            meta[module_name].append({
                "name": function,
                "arguments": args,
                "options": opts,
                "callback": getattr(module, function)
            })

    main_group = create_dynamic_group('cli', [])
    if target is not None:
        keys = meta.keys()
        for key in keys:
            main_group.add_command(create_dynamic_group(key, meta[key]))
    else:
        main_group = create_dynamic_group('cli', meta[list(meta.keys())[0]])

    return main_group