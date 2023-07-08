import importlib
from os import listdir
from .decorators import *
from ast import parse, FunctionDef, Import, ImportFrom
from importlib.util import spec_from_file_location, module_from_spec, find_spec
from os.path import dirname, join, exists, abspath, splitext, basename


def parse_nodes(entry: str, target: str):

    def check_if_my_decorators(my_imports, node):
        decorator_list = []
        if hasattr(node, "decorator_list"):
            for decorator in getattr(node, "decorator_list"):
                if hasattr(decorator, "attr") and decorator.attr \
                        in globals() and globals()[decorator.attr].__module__ \
                        == "impose_cli.decorators" and decorator.attr in my_imports["to"]:
                    decorator_list.append(decorator.attr)
                elif not hasattr(decorator, "attr") and hasattr(decorator, "id") \
                        and decorator.id in globals() and globals()[decorator.id].__module__ \
                        == "impose_cli.decorators" and decorator.id in my_imports["from"]:
                    decorator_list.append(decorator.id)
        return decorator_list

    def analyze_file(python_file: str):
        tree = parse(open(python_file, "r").read())

        imports = {
            "direct": [],
            "from": []
        }

        data = []
        for node in tree.body:
            if isinstance(node, ImportFrom):
                for name in node.names:
                    imports["from"].append(name.name if name.asname is None else name.asname)
            elif isinstance(node, Import):
                for name in node.names:
                    imports["direct"].append(name.name if name.asname is None else name.asname)
            elif isinstance(node, FunctionDef):
                decorator_list = check_if_my_decorators(imports, node)
                data.append({
                    name
                })

        return 1

    def load_module_from_file(file_path):
        module_name = splitext(basename(entry))[0] \
            if target is None else \
            "{}{}".format(target, file_path.split(target)[-1]).replace("/", "-").replace(".py", "").replace("_", "-")
        spec = spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module_name

    def produce_module_map(python_modules_files: list[str]):
        meta = {}
        meta["s"] = 1
        for file in python_modules_files:
            module, module_name = load_module_from_file(file)
            analysis = analyze_file(file)
            meta[module_name] = []
        return meta

    def find_files():
        if target is None:
            return [entry]

        else:
            directory = join(dirname(entry), target)
        if not exists(directory):
            raise FileNotFoundError(f"There is no directory {directory}.")

        dirs = [x for x in listdir(directory) if x.endswith('.py')]
        return [abspath(join(directory, f)) for f in dirs]

    files = find_files()
    meta = produce_module_map(files)
    z = 1

