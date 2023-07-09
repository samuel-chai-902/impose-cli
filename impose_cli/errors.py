

class InterfaceNotImplementedError(NotImplementedError):
    def __init__(self, interface_type):
        super().__init__(f"impose_cli does not currently have a {interface_type} interface.")