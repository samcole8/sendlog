class EndpointVariableMismatchError(Exception):
    def __init__(self, dest, endpoint, expected_vars, got_vars):
        super().__init__(f"Invalid configuration file: Endpoint plugin '{endpoint}' did not receive the expected variable(s) '{expected_vars}' from destination '{dest}'; got '{got_vars}' instead.")
