# Endpoint-specific errors

class MissingVariableError(Exception):
    """Custom exception for missing required variables."""
    def __init__(self, dest, endpoint, missing_vars):
        self.missing_vars = missing_vars
        super().__init__(f"Invalid configuration file: Endpoint plugin '{endpoint}' did not receive the expected variable(s) '{missing_vars}' from destination '{dest}'.")

class UnexpectedVariableError(Exception):
    """Custom exception for invalid endpoint variable."""
    def __init__(self, dest, endpoint, key):
        self.key = key
        super().__init__(f"Invalid configuration file: Endpoint plugin '{endpoint}' received unexpected '{key}' variable from destination '{dest}'.")
