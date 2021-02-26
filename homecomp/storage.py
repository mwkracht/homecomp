import json
import operator
import os
import shutil
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Iterator
from typing import Dict

from homecomp import errors
from homecomp.models import HousingDetail
from homecomp.models import PurchaserProfile


@dataclass
class DataclassStorageTable:
    table_cls: type
    id_field: str
    entries: Dict = field(default_factory=dict)

    def __iter__(self):
        return (self.table_cls(**row) for row in self.entries.values())

    def _entry_id(self, entry):
        try:
            return getattr(entry, self.id_field)
        except AttributeError as error:
            raise errors.IllegalEntry(f'Cannot find id field {self.id_field} on entry') from error

    def find(self, entry_id: str, match: callable = operator.contains) -> Any:
        """Find first entry which either matches or contained provided id string"""
        try:
            return next(self.find_all(entry_id, match))
        except StopIteration as error:
            raise errors.NoEntryFound(f'No entries found which match {entry_id}') from error

    def find_all(self, entry_id: str, match: callable = operator.contains) -> Iterator[Any]:
        """Find all entries which either matches or contained provided id string"""
        return (
            self.table_cls(**entry)
            for entry in self.entries.values()
            if match(entry[self.id_field], entry_id)
        )

    def delete(self, entry_id: str):
        """Remove entry which has the exact match fo the provided entry id"""
        try:
            return self.entries.pop(entry_id)
        except KeyError as error:
            raise errors.NoEntryFound(f'No entries found which match {entry_id}') from error

    def save(self, entry: Any, overwrite: bool = True):
        entry_id = self._entry_id(entry)

        if entry_id in self.entries and not overwrite:
            raise errors.EntryExists(f'Item {entry} already exists in storage table')

        self.entries[entry_id] = asdict(entry)


class DataclassFileStorage:

    table_map = {
        'housing': (HousingDetail, 'name'),
        'profiles': (PurchaserProfile, 'name')
    }

    def __init__(self, filename='.storage'):
        self.filename = filename
        self.data = {}

    def __getattr__(self, item):
        if item in self.table_map:
            if item not in self.data:
                self.data[item] = {}

            # pass mutable list so that storage table modifications are
            # reflected in self.data
            return DataclassStorageTable(
                *self.table_map[item],
                self.data[item]
            )

        raise AttributeError(f'{type(self)} object has no attribute {item}')

    def __enter__(self):
        try:
            with open(self.filename, 'r') as storage_fd:
                self.data = json.loads(storage_fd.read())
        except FileNotFoundError:
            with open(self.filename, 'w') as storage_fd:
                storage_fd.write(json.dumps(self.data))

        return self

    def __exit__(self, *args, **kwargs):
        backup_filename = f'{self.filename}.backup'
        shutil.copy(self.filename, backup_filename)

        try:
            with open(self.filename, 'w') as storage_fd:
                storage_fd.write(json.dumps(self.data))
        except:
            shutil.move(backup_filename, self.filename)
            raise
        else:
            os.remove(backup_filename)
