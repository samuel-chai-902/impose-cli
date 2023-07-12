from ._utils import parse_nodes, _get_interface_builder
from inspect import stack, getframeinfo, currentframe


def impose_cli(target: str = None, launch_type: str = "cli", launch_specific_configs: dict = {},
               return_before_executing: bool = False, root_name: str = "cli", build_cache: bool = True):
    """
    The entrypoint for building a suite of CLI commands / API endpoints.
    :param launch_specific_configs:
    :param target: Can be used to specify the relative path of a directory which will contain all commands / endpoints.
    :param launch_type: CLI or API.
    :param return_before_executing: Return the produced object before executing.
    :param build_cache: If cache should be built. This could be problematic for larger applications.
    :return:
    """
    entry = stack()[1].filename
    tree = parse_nodes(entry, target)
    return _get_interface_builder(tree, launch_type, root_name, launch_specific_configs, return_before_executing)

