from .decorators import *  # Do not remove this import
import os
import inspect
import builtins
import click
from docstring_parser import parse as docparse
from inspect import signature as sig
from ast import parse, FunctionDef, Import, ImportFrom, unparse
from importlib.util import spec_from_file_location, module_from_spec
from os.path import dirname, join, exists, abspath, splitext, basename, relpath

_SUPPORTED_TYPES = [str, int, list, dict]


def parse_nodes(entry: str, target: str):
    class Function(object):
        def __init__(self, name, function_info: dict):
            self.name = name
            self.arguments = function_info["arguments"]
            self.options = function_info["options"]
            self.decorators = function_info["decorators"]
            self.long_description = function_info["long_description"]
            self.short_description = function_info["short_description"]
            self.reference = function_info["reference"]

    class Node(object):
        def __init__(self, name: str):
            self.root = False
            self.name = name
            if self.name is None:
                self.root = True
            self.functions = []
            self.children = []
            self.external_object = None

        def add_child(self, child):
            self.children.append(child)

        def add_function(self, function_info):
            self.functions.append(Function(**function_info))

        def alter_children(self, callback):
            for child in self.children:
                callback(child, self.external_object)

    class Tree(object):
        def __init__(self, root: Node):
            self.root = root

        def add_func(self, path: str, func_info):
            parts = path.split("/")
            node = self.root
            for i in range(1, len(parts)):
                matching_node = next((x for x in node.children if x.name == parts[i]), None)
                if matching_node is None:
                    matching_node = Node(name=parts[i])
                    node.add_child(matching_node)
                node = matching_node
            node.add_function(func_info)

    def build_tree(node_info: dict):
        rel_path_start = entry if target is None else join(dirname(entry), target)
        relative_dict = {
            "/{}".format(relpath(x, rel_path_start).replace(".py", "").replace("_", "-").replace(".", "")): y for x, y
            in node_info.items()}
        tree = Tree(Node(None))
        list_of_tuples = []
        for file, func_info in relative_dict.items():
            for func in func_info:
                list_of_tuples.append((file, {
                    "name": func,
                    "function_info": relative_dict[file][func]
                }))
        for x, y in list_of_tuples:
            tree.add_func(x, y)
        return tree

    def extract_meta(node: FunctionDef, doc, module):
        parameter_meta = {}
        doc_meta = {}
        if doc is not None and hasattr(doc, "params") and getattr(doc, "params") is not None:
            for param in doc.params:
                doc_meta[param.arg_name] = param.description
        if hasattr(node, "args") and getattr(node, "args") is not None and len(getattr(node, "args").args) > 0:
            args_object = getattr(node, "args")
            arg_list = args_object.args
            for arg in arg_list:
                parameter_meta[arg.arg] = {}
                if hasattr(arg, "annotation") and getattr(arg, "annotation") is not None:
                    parameter_meta[arg.arg]["type"] = unparse(getattr(arg, "annotation"))
                else:
                    parameter_meta[arg.arg]["type"] = "Any"
                parameter_settings = sig(getattr(module, node.name)).parameters.get(arg.arg)
                if hasattr(parameter_settings, "default"):
                    parameter_meta[arg.arg]["default"] = parameter_settings.default
                if arg.arg in doc_meta:
                    parameter_meta[arg.arg]["description"] = doc_meta[arg.arg]
        return parameter_meta

    def check_if_my_decorators(my_imports, node):
        decorator_list = []
        if hasattr(node, "decorator_list"):
            for decorator in getattr(node, "decorator_list"):
                if hasattr(decorator, "attr") and decorator.attr \
                        in globals() and globals()[decorator.attr].__module__ \
                        == "impose_cli.decorators" and "impose_cli" in my_imports["direct"]:
                    decorator_list.append(decorator.attr)
                elif not hasattr(decorator, "attr") and hasattr(decorator, "id") \
                        and decorator.id in globals() and globals()[decorator.id].__module__ \
                        == "impose_cli.decorators" and decorator.id in my_imports["from"]:
                    decorator_list.append(decorator.id)
        return decorator_list

    def analyze_file(python_file: str, module):
        tree = parse(open(python_file, "r").read())

        imports = {
            "direct": [],
            "from": []
        }

        data = {}
        for node in tree.body:
            if isinstance(node, ImportFrom):
                for name in node.names:
                    imports["from"].append(name.name if name.asname is None else name.asname)
            elif isinstance(node, Import):
                for name in node.names:
                    imports["direct"].append(name.name if name.asname is None else name.asname)
            elif isinstance(node, FunctionDef):
                reference = getattr(module, node.name)
                doc = inspect.getdoc(getattr(module, node.name))
                long_description = None
                short_description = None
                if doc is not None:
                    doc = docparse(doc)
                    short_description = doc.short_description
                    long_description = doc.long_description
                decorator_list = check_if_my_decorators(imports, node)
                meta = extract_meta(node, doc, module)
                options = {}
                arguments = {}
                for parameter_name in meta.keys():
                    if "default" in meta[parameter_name]:
                        options[parameter_name] = meta[parameter_name]
                    else:
                        arguments[parameter_name] = meta[parameter_name]
                data[node.name] = {
                    "arguments": arguments,
                    "options": options,
                    "long_description": long_description,
                    "short_description": short_description,
                    "decorators": decorator_list,
                    "reference": reference
                }
        return data

    def load_module_from_file(file_path):
        module_name = splitext(basename(entry))[0] \
            if target is None else \
            "{}{}".format(target, file_path.split(target)[-1]).replace("/", "-").replace(".py", "").replace("_", "-")
        spec = spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, module_name

    def produce_module_map(python_modules_files: list[str]):
        file_function_map = {}
        for file in python_modules_files:
            module, module_name = load_module_from_file(file)
            analysis = analyze_file(file, module)
            if "_settings" in analysis and "impose" in analysis["_settings"]["decorators"]:
                for function_name in analysis.keys():
                    if "impose" not in analysis[function_name]["decorators"] and "hide" not in analysis[function_name][
                        "decorators"]:
                        analysis[function_name]["decorators"].append("impose")
            file_function_map[file] = {x: y for x, y in analysis.items() if
                                       "impose" in y["decorators"] and x != "_settings"}
        return file_function_map

    def find_files():
        if target is None:
            return [entry]

        else:
            directory = join(dirname(entry), target)
        if not exists(directory):
            raise FileNotFoundError(f"There is no directory {directory}.")

        dirs = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if
                file.endswith('.py')]
        return [abspath(join(directory, f)) for f in dirs]

    files = find_files()
    meta = produce_module_map(files)
    tree = build_tree(meta)
    if len(tree.root.children) == 1 and not len(tree.root.functions) and tree.root.children[0].name == "":
        tree.root = tree.root.children[0]
        tree.root.root = True
    return tree


def build_cli_with_tree(tree, root_name=None, return_before_executing=False):
    def get_types(type_name):
        # Import custom logic here
        return hasattr(builtins, type_name) and isinstance(getattr(builtins, type_name), type).__name__

    def create_command(function):
        command = click.Command(
            name=function.name.replace("_", "-"),
            callback=function.reference,
            short_help=function.short_description,
            help=function.long_description
        )

        for arg, config in function.arguments.items():
            click_configurations = {}
            if "default" in config:
                click_configurations["default"] = config["default"]
            if "type" in config and config["type"] != "Any":
                click_configurations["type"] = config["type"]
            if "default" not in config and "require_flags" in function.decorators:
                config["required"] = True
            if "description" in config:
                config["help"] = config["description"]
            if "default" in config:
                command.params.append(click.Option((arg,), **click_configurations))
            else:
                if "required_flags" in function.decorators:
                    command.params.append(click.Option((arg,), **click_configurations))
                else:
                    command.params.append(click.Argument((arg,), **click_configurations))

        return command

    def handle_child(child, parent_group):
        child_group = click.Group(name=child.name)
        parent_group.add_command(child_group)
        child.external_object = child_group
        for function in child.functions:
            child_group.add_command(create_command(function))
        if child is not None and child.children is not None and len(child.children) > 0:
            child.alter_children(handle_child)

    def dft(root):
        cli = click.Group(name="root")
        root.external_object = cli
        for function in root.functions:
            cli.add_command(create_command(function))
        root.alter_children(handle_child)
        return cli

    res = dft(tree.root)
    if not return_before_executing:
        return res
    else:
        res()


def build_api_with_tree(tree, root_name=None, return_before_executing=False, host="0.0.0.0", port=8000):
    import fastapi
    import uvicorn
    api = fastapi.FastAPI()

    def create_endpoint(router, function):
        @router.get(("/{}".format(function.name) if not function.name.startswith("/") else function.name))
        def dynamic_route():
            return function.reference

        return router

    def handle_child(child, parent_group):
        child_group = fastapi.APIRouter(prefix="/{}".format(child.name).replace("//", "/"))
        parent_group.add_command(child_group)
        child.external_object = child_group
        for function in child.functions:
            pass
        if child is not None and child.children is not None and len(child.children) > 0:
            child.alter_children(handle_child)

    def dft(root):
        base_route = fastapi.APIRouter()
        root.external_object = base_route
        for function in root.functions:
            create_endpoint(base_route, function)
        root.alter_children(handle_child)
        api.include_router(base_route)
        return api

    res = dft(tree.root)
    if return_before_executing:
        return res
    else:
        uvicorn.run(res, host=host, port=port)
