"""Custom exception definitions for use throughout the application."""

import logging
from abc import ABC

from utils.log import write, config

class SendlogError(Exception, ABC):
    """Base error class."""
    def __init__(self):
        self.logger = logging.getLogger()
        self._level = logging.critical
        self._code_parts = []
        self._message_parts = []
        self._data = {}

    @property
    def level(self):
        return self._level
    
    @level.setter
    def level(self, value):
        self._level = value

    @property
    def code(self):
        return ".".join(self._code_parts)
    
    @code.setter
    def code(self, code: str):
        self._code_parts.append(code)
    
    @property
    def message(self):
        return ": ".join(self._message_parts)
    
    @message.setter
    def message(self, message: str):
        self._message_parts.append(message)
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data

    def log(self):
        # Log exception
        write(self.level, self.code, self.message, **self.data)
    
    def __str__(self):
        """Return error message based on subclass implementation."""
        return f"[{self.code}] {self.message}"

# Startup-related workflow errors

class WorkflowError(SendlogError, ABC):
    """Base exception for workflow-related errors."""
    def __init__(self):
        super().__init__()
        self.message = "An error occurred while building a workflow"
        self.code = "WORKFLOW"

class EndpointVariableMismatchError(WorkflowError):
    def __init__(self, endpoint_name: str, channel_name: str, required_keys: set, received_keys: set):
        super().__init__()
        self.code = "ENDPOINT_VARIABLE_MISMATCH"
        self.message = (
            f"Channel plugin class '{channel_name}' did not receive the expected variable(s) "
            f"'{required_keys}' from endpoint '{endpoint_name}'; got '{received_keys}' instead"
        )
        self.data = {
            "endpoint_name": endpoint_name,
            "channel_name": channel_name,
            "required_keys": required_keys,
            "received_keys": received_keys
        }
        self.log()

class PluginClassNotFoundError(WorkflowError):
    def __init__(self, plugin_class_name, parent_fullname: str):
        super().__init__()
        self.code = "PLUGIN_CLASS_NOT_FOUND"
        self.message = f"Referenced plugin class '{plugin_class_name}' could not be found in '{parent_fullname}'"
        self.data = {
            "plugin_class_name": plugin_class_name,
            "parent_fullname": parent_fullname
            }
        self.log()

class PluginModuleNotFoundError(WorkflowError):
    def __init__(self, plugin_fullname: str):
        super().__init__()
        self.code = "PLUGIN_MODULE_NOT_FOUND"
        self.message = f"Referenced plugin module '{plugin_fullname}' could not be found"
        self.data = {"plugin_fullname": plugin_fullname}
        self.log()

class PluginInheritanceError(WorkflowError):
    def __init__(self, plugin_class_fullname: str, plugin_base_class_name: str, plugin_class_bases: list):
        super().__init__()
        self.code = "PLUGIN_INHERITANCE"
        self.message = f"Plugin class '{plugin_class_fullname}' was rejected because it did not inherit from the expected base class '{plugin_base_class_name}'; instead, got: '{plugin_class_bases}'"
        self.data = {
            "plugin_class_fullname": plugin_class_fullname,
            "plugin_base_class_name": plugin_base_class_name,
            "plugin_class_bases": plugin_class_bases
        }
        self.log()

class EndpointUndefinedError(WorkflowError):
    def __init__(self, endpoint_name: str, worktree_file_path: str):
        super().__init__()
        self.code = "ENDPOINT_UNDEFINED"
        self.message = f"Endpoint '{endpoint_name}' referenced by in worktree for '{worktree_file_path}' is not defined in the 'endpoints' section"
        self.data = {
            "endpoint_name": endpoint_name,
            "worktree_file_path": worktree_file_path
        }
        self.log()

# Startup-related config errors

class ConfigError(SendlogError, ABC):
    """Base exception for config-related errors."""
    def __init__(self):
        super().__init__()
        self.message = "An error occurred while loading the configuration file"
        self.code = "CONFIG"

class ConfigKeyError(ConfigError):
    def __init__(self, key):
        super().__init__()
        self.code = "KEY"
        self.message = f"Expected key '{key}' could not be found"
        self.data = {"key": key}
        self.log()

class ConfigTypeError(ConfigError):
    def __init__(self, expected_type, received_type):
        super().__init__()
        self.code = "TYPE"
        self.message = f"Expected type '{expected_type}' but received '{received_type}' instead"
        self.data = {
            "expected_type": expected_type,
            "recieved_type": received_type}
        self.log()


# Plugin definition errors

class PluginError(SendlogError, ABC):
    """Base exception for plugin-related errors."""
    def __init__(self):
        super().__init__()
        self.message = "An error occurred in a plugin definition"
        self.code = "PLUGIN"

class PluginOverrideError(PluginError):
    def __init__(self, plugin_class_name: str, member_name: str):
        super().__init__()
        self.code = "OVERRIDE"
        self.message =  f"Plugin subclass '{plugin_class_name}' was rejected because it attempted to override core member '{member_name}'"
        self.data = {
            "plugin_class_name": plugin_class_name,
            "member_name": member_name
        }
        self.log()

class PluginInitError(PluginError):
    def __init__(self, plugin_class_name, params):
        super().__init__()
        self.code = "INIT_VALIDATION"
        self.message =  f"Plugin subclass '{plugin_class_name}' was rejected because the '__init__' method contained a parameter other than 'self'; got '{params}' instead"
        self.data = {
            "plugin_class_name": plugin_class_name,
            "params": params
        }
        self.log()

# Workflow-fatal runtime errors

class RuntimeError(SendlogError, ABC):
    def __init__(self):
        super().__init__()
        self.code = "RUNTIME"
        self.message = "An error occurred that prevented an alert from sending"
        self._level = logging.error

class RuleError(RuntimeError, ABC):
    def __init__(self, plugin_class_name, exc_info, log_line, file_path, workflow_tracestack):
        super().__init__()
        self.code = "RULE_ERROR"
        self.message =  f"Rule plugin subclass '{plugin_class_name}' encountered the following error when processing the log line '{log_line}' from file '{file_path}': '{type(exc_info).__name__}: {exc_info}'"
        self.data = {
            "plugin_class_name": plugin_class_name,
            "log_line": log_line,
            "workflow_trace_stack": workflow_tracestack,
            "file_path": file_path,
            "exc_info": exc_info
        }
        self.log()

class TransformerError(RuntimeError, ABC):
    def __init__(self, plugin_class_name, exc_info, log_line, file_path, workflow_tracestack):
        super().__init__()
        self.code = "TRANSFORMER_ERROR"
        self.message =  f"Transformer plugin subclass '{plugin_class_name}' encountered athe following error when processing the log line '{log_line}' from file '{file_path}': '{type(exc_info).__name__}: {exc_info}'"
        self.data = {
            "plugin_class_name": plugin_class_name,
            "log_line": log_line,
            "workflow_trace_stack": workflow_tracestack,
            "file_path": file_path,
            "exc_info": exc_info
        }
        self.log()

class EndpointError(RuntimeError, ABC):
    def __init__(self, endpoint_name, plugin_class_name, exc_info, log_line, file_path, workflow_tracestack):
        super().__init__()
        self.code = "ENDPOINT_ERROR"
        self.message =  f"Endpoint '{endpoint_name}' from Channel plugin subclass '{plugin_class_name}' encountered the following error when processing the alert input '{log_line}' from file '{file_path}': '{type(exc_info).__name__}: {exc_info}'"
        self.data = {
            "endpoint_name": endpoint_name,
            "plugin_class_name": plugin_class_name,
            "log_line": log_line,
            "workflow_trace_stack": workflow_tracestack,
            "file_path": file_path,
            "exc_info": exc_info
        }
        self.log()