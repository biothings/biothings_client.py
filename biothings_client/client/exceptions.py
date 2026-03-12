"""Custom exceptions for the clients (async and sync)."""


class OptionalDependencyImportError(ImportError):
    def __init__(
        self, optional_function_access: str, optional_group: str, libraries: list[str]
    ) -> None:
        pip_command = f"`pip install biothings_client[{optional_group}]`"
        message = (
            f"To {optional_function_access} requires the {libraries} library(ies). "
            f"To install run the following command: {pip_command}"
        )
        super().__init__(message)


class CachingNotSupportedError(Exception):
    pass
