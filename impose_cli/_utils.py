import os
import inspect
import builtins
import astor
import click
from .errors import InterfaceNotImplementedError
from docstring_parser import parse as docparse
from inspect import signature as sig
from ast import parse, FunctionDef, Import, ImportFrom
from importlib.util import spec_from_file_location, module_from_spec
from os.path import dirname, join, exists, abspath, splitext, basename, relpath
from . import decorators as imposedecorators


def parse_nodes(entry: str, target: str):
    class Function(object):
        def __init__(self, name, function_info: dict):
            self.name = name
            self.arguments = function_info["arguments"]
            self.decorators = function_info["decorators"]
            self.long_description = function_info["long_description"]
            self.short_description = function_info["short_description"]
            self.reference = function_info["reference"]

    class Node(object):
        def __init__(self, name: str = None):
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
                callback(child, self)

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
        parse_tree = Tree(Node())
        list_of_tuples = []
        for file, func_info in relative_dict.items():
            for func in func_info:
                list_of_tuples.append((file, {
                    "name": func,
                    "function_info": relative_dict[file][func]
                }))
        for x, y in list_of_tuples:
            parse_tree.add_func(x, y)
        return parse_tree

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
                    parameter_meta[arg.arg]["type"] = astor.to_source(getattr(arg, "annotation")).strip()
                else:
                    parameter_meta[arg.arg]["type"] = "Any"
                parameter_settings = sig(getattr(module, node.name)).parameters.get(arg.arg)
                if hasattr(parameter_settings, "default") and \
                        str(getattr(parameter_settings, "default")) != "<class 'inspect._empty'>":
                    parameter_meta[arg.arg]["default"] = parameter_settings.default
                if arg.arg in doc_meta:
                    parameter_meta[arg.arg]["description"] = doc_meta[arg.arg]
        return parameter_meta

    def check_if_my_decorators(my_imports, node):
        module_attributes = dir(imposedecorators)
        decorator_list = []
        if hasattr(node, "decorator_list"):
            for decorator in getattr(node, "decorator_list"):
                if hasattr(decorator, "attr") and hasattr(module_attributes, decorator.attr)\
                        and "impose_cli" in my_imports["direct"]:
                    decorator_list.append(decorator.attr)
                elif not hasattr(decorator, "attr") and hasattr(decorator, "id") \
                        and hasattr(imposedecorators, decorator.id) and decorator.id in my_imports["from"]:
                    decorator_list.append(decorator.id)
        return decorator_list

    def analyze_file(python_file: str, module):
        ast_tree = parse(open(python_file, "r").read())

        imports = {
            "direct": [],
            "from": []
        }

        data = {}
        for node in ast_tree.body:
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
                function_meta = extract_meta(node, doc, module)
                data[node.name] = {
                    "arguments": function_meta,
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
                    if "impose" not in analysis[function_name]["decorators"] and \
                            "hide" not in analysis[function_name]["decorators"]:
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
    if len(tree.root.children) == 1 and not len(tree.root.functions) and (tree.root.name == "" or tree.root.name is None):
        tree.root = tree.root.children[0]
        tree.root.root = True
    return tree


class InterfaceBuilder(object):
    def __init__(self, tree, root_name: str, config: dict = None):
        self.tree = tree
        self.config = config
        self.root_name = root_name

    def dfs(self):
        self.initialize_root()
        root = self.tree.root
        for function in root.functions:
            self.handle_vertex(root, function)
        root.alter_children(type(self).handle_edge)

    def initialize_root(self):
        pass

    @staticmethod
    def handle_edge(node, parent):
        pass

    @staticmethod
    def handle_vertex(node, function):
        pass

    def run(self):
        self.tree.root.external_object()


class CLIInterfaceBuilder(InterfaceBuilder):
    def initialize_root(self):
        name = "cli" if self.tree.root.name == "" and self.root_name is None else self.root_name
        self.tree.root.external_object = click.Group(name=name)

    @staticmethod
    def handle_vertex(node, function):
        command = click.Command(
            name=function.name.replace("_", "-"),
            callback=function.reference,
            short_help=function.short_description,
            help=function.long_description
        )
        for arg, meta in function.arguments.items():
            config = {}
            if "default" in meta:
                config["default"] = meta["default"]
            if "type" in meta and meta["type"] != "Any":
                config["type"] = getattr(builtins, meta["type"])
            if "default" not in meta and "require_flags" in function.decorators:
                config["required"] = True
            if "description" in meta and "default" in meta or "require_flags" in function.decorators:
                config["help"] = meta["description"]
            command.params.append(
                click.Option((f"--{arg}",), **config) if "default" in meta or "require_flags" in function.decorators else click.Argument((arg,), **config)
            )
        node.external_object.add_command(command)

    @staticmethod
    def handle_edge(node, parent):
        node.external_object = click.Group(name=node.name)
        parent.external_object.add_command(node.external_object)
        for function in node.functions:
            CLIInterfaceBuilder.handle_vertex(node, function)
        if node is not None and node.children is not None and len(node.children) > 0:
            node.alter_children(CLIInterfaceBuilder.handle_edge)

    def run(self):
        self.tree.root.external_object()


def _get_interface_builder(tree, interface_type, root_name, config, return_before_executing):
    builder_name = "{}InterfaceBuilder".format(interface_type.upper())
    if builder_name in globals():
        builder = globals()[builder_name](tree, root_name, config)
        builder.dfs()
        if return_before_executing:
            return builder.tree.root.external_object
        else:
            builder.run()
    else:
        raise InterfaceNotImplementedError(interface_type)
