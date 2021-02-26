class ClientError(Exception):
    """Generic client exception"""


class CaptchaError(ClientError):
    """Raised on client responses that include captcha verifications"""


class ClientNotSupported(ClientError):
    """Raised when making a request to a URL with no client"""


class StorageError(Exception):
    """Generic storage exception"""


class IllegalEntry(StorageError):
    """Storage entry that does not contain an ID field"""


class NoEntryFound(StorageError):
    """Raised when attempting to access non-existent storage entry"""


class EntryExists(StorageError):
    """Raised if entry already exists when adding a new entry to storage"""
