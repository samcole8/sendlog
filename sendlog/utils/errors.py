# Base error

class SendlogError(Exception):
    def __init__(self, code, msg):
        super().__init__(f"[{f"SENDLOG.{code}"}]: {msg}")

# Workflow errors that occur when loading a workflow

class WorkflowError(SendlogError):
    def __init__(self, code, msg):
        super().__init__(f"WORKFLOW.{code}", f"An error occurred while building workflows from the configuration file: {msg}")

class EndpointVariableMismatchError(WorkflowError):
    def __init__(self, dest, endpoint, expected_vars, got_vars):
        msg = (f"Endpoint plugin '{endpoint}' did not receive the expected variable(s) "
               f"'{expected_vars}' from destination '{dest}'; got '{got_vars}' instead.")
        super().__init__("ENDPOINT_VARIABLE_MISMATCH", msg)

class PluginModuleNotFoundError(WorkflowError):
    def __init__(self, plugin):
        super().__init__("PLUGIN_MODULE_NOT_FOUND", f"The referenced plugin module '{plugin}' does not exist.")

class PluginClassNotFoundError(WorkflowError):
    def __init__(self, class_name, parent):
        super().__init__("PLUGIN_CLASS_NOT_FOUND", f"The referenced plugin class '{class_name}' does not exist within parent class '{parent}'.")

class DestinationUndefinedError(WorkflowError):
    def __init__(self, dest_name):
        super().__init__("DESTINATION_UNDEFINED_ERROR", f"The referenced destination '{dest_name}' is undefined.")

class PluginInheritanceError(WorkflowError):
    def __init__(self, class_name, base_class_name, bases):
        super().__init__("PLUGIN_INHERITANCE_ERROR", f"The plugin class '{class_name}' was rejected because it didn't inherit from the expected base class '{base_class_name}'. Instead, got '{bases}'.")

# Config errors that occur when loading the configuration file

class ConfigurationError(SendlogError):
    def __init__(self, code, msg):
        super().__init__(f"CONFIG.{code}", f"An error occurred while parsing the configuration file: {msg}")

class ConfigurationKeyError(ConfigurationError):
    def __init__(self, key):
        super().__init__("KEY_NOT_FOUND", f"Expected key '{key}' could not be found.")

class ConfigurationTypeError(ConfigurationError):
    def __init__(self, expected, got):
        super().__init__("UNEXPECTED_TYPE", f"Expected '{expected}' but got '{got}'.")

# Plugin errors that occur when importing a plugin

class PluginError(SendlogError):
    def __init__(self, code, msg):
        super().__init__(f"WORKFLOW.{code}", f"An error occurred in a plugin definition: {msg}")

class PluginOverrideError(PluginError):
    def __init__(self, subclass, member):
        super().__init__("PLUGIN_OVERRIDE", f"Plugin subclass '{subclass}' was rejected because it attempted to override core member '{member}'.")

class PluginHierarchyError(PluginError):
    def __init__(self, subclass, member):
        super().__init__("PLUGIN_HIERARCHY", f"Plugin subclass '{subclass}' was rejected because it was defined in an unexpected place '{member}'")

# Worker runtime errors that occur when sending an alert

class WorkerError(SendlogError):
    def __init__(self, code, msg):
        super().__init__(f"WORKER.{code}", f"{msg}")

class DestinationError(WorkerError):
    def __init__(self, endpoint, details):
        super().__init__("ENDPOINT", f"An error occurred when sending an alert via destination '{endpoint}'. Details: {details}")

class RuleError(WorkerError):
    def __init__(self,  plugin,lm, e):
        super().__init__("RULE", f"An error occurred during evaluation of message '{lm}' via rule '{plugin}'. Details: {e}")

class TransformerError(WorkerError):
    def __init__(self, plugin):
        super().__init__("TRANSFORMER", f"An error occurred in transformer '{plugin}'. Details: ")
