class StorageError(Exception):
    """Generic storage exception"""


class IllegalEntry(StorageError):
    """Storage entry that does not contain an ID field"""


class NoEntryFound(StorageError):
    """Raised when attempting to access non-existent storage entry"""


class EntryExists(StorageError):
    """Raised if entry already exists when adding a new entry to storage"""
