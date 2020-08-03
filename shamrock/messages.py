"""Global Shamrock message strings."""

INSTANCE: str = (
    "An instance of Shamrock API integration for Trefle service with token id: "
    "'{token}', querying version: '{version}'"
)
EXCEPTION_TIMEOUT: str = "The request timed out."
EXCEPTION_REDIRECTS: str = "The request had too many redirects."
EXCEPTION_JSON: str = "Invalid JSON in response."
EXCEPTION_UNKNOWN: str = "Unknown exception raised: {exception}"
EXCEPTION_ARGUMENT_VALUE: str = "The parameter '{parameter}' can only be {values}."
