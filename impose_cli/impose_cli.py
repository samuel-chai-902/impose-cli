from ._utils import parse_nodes
from inspect import currentframe, getframeinfo


def impose_cli(target: str = None, launch_type: str = "cli", return_before_executing: bool = False, build_cache: bool = True):
    """
    The entrypoint for building a suite of CLI commands / API endpoints.
    :param target: Can be used to specify the relative path of a directory which will contain all commands / endpoints.
    :param launch_type: CLI or API.
    :param return_before_executing: Return the produced object before executing.
    :param build_cache: If cache should be built. This could be problematic for larger applications.
    :return:
    """

    nodes = parse_nodes(getframeinfo(currentframe().f_back)[0], target)
    z = 1