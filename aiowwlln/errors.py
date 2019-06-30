"""Define package errors."""


class WWLLNError(Exception):
    """Define a base error."""

    pass


class RequestError(WWLLNError):
    """Define an error related to invalid requests."""

    pass
