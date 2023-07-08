from ._utils import *
from inspect import currentframe, getframeinfo


def impose_cli(target: str = None, launch_type: str = "cli", launch_specific_configs: dict = {},
               return_before_executing: bool = False, build_cache: bool = True):
    """
    The entrypoint for building a suite of CLI commands / API endpoints.
    :param launch_specific_configs:
    :param target: Can be used to specify the relative path of a directory which will contain all commands / endpoints.
    :param launch_type: CLI or API.
    :param return_before_executing: Return the produced object before executing.
    :param build_cache: If cache should be built. This could be problematic for larger applications.
    :return:
    """

    tree = parse_nodes(getframeinfo(currentframe().f_back)[0], target)
    app = None
    if "build_{}_with_tree".format(launch_type) in globals():
        app = globals()["build_{}_with_tree".format(launch_type)](
            tree,
            return_before_executing,
            **(launch_specific_configs["{}_config".format(launch_type)] if launch_type in launch_specific_configs else {})
        )
    else:
        raise NotImplementedError(f"impose_cli does not run as an {launch_type}.")
    return app
