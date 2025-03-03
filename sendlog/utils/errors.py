# Workflow Errors

class EndpointVariableMismatchError(Exception):
    def __init__(self, dest, endpoint, expected_vars, got_vars):
        super().__init__(f"Invalid configuration file: Endpoint plugin '{endpoint}' did not receive the expected variable(s) '{expected_vars}' from destination '{dest}'; got '{got_vars}' instead.")

class PluginModuleNotFoundError(Exception):
    def __init__(self, plugin):
        super().__init__(f"Invalid configuration file: The referenced plugin module '{plugin}' does not exist.")

class PluginClassNotFoundError(Exception):
    def __init__(self, child, parent):
        super().__init__(f"Invalid configuration file: The referenced plugin class '{child}' does not exist within the specified parent '{repr(parent)}'.")

class DestinationUndefinedError(Exception):
    def __init__(self, dest_name):
        super().__init__(f"Invalid configuration file: The referenced destination '{dest_name}' is undefined.")
