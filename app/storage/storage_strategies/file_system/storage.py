import os

class FileSystemStorage():
    """
    A file-based implementation of the AbstractStorage interface.

    Each entity is stored in a dedicated folder, named after its identifier.
    Inside that folder, we store one JSON file (entity.json) with the entire
    state: identifier, object type, properties, and relationships.
    """

    def __init__(self, storage_dir: str = "storage_data"):
        self._storage_dir = storage_dir
        os.makedirs(self._storage_dir, exist_ok=True)