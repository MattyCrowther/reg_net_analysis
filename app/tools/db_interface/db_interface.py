import os
import json

from app.tools.db_interface.databases.regulondb import RegulonDB
from app.tools.db_interface.databases.abstract_database import AbstractObject
from app.tools.db_interface.databases.abstract_database import PhysicalEntity
from app.tools.db_interface.databases.abstract_database import ConceptualEntity
storage_file = "existing_data.json"

class DatabaseInterface:
    def __init__(self):
        self._handlers = [RegulonDB()]
    
    def download_all(self,refresh=False):
        all_records = self._load_records()
        if refresh:
            results = []
            for handler in self._handlers:
                results += handler.fetch_all()
            all_records = self._merge_records(results,
                                              all_records)
        pe = []
        ce = []
        for item in all_records:
            if isinstance(item,PhysicalEntity):
                pe.append(item)
            elif isinstance(item,ConceptualEntity):
                ce.append(item)
            else:
                raise ValueError(type(item))
        return pe,ce
    
    def _merge_records(self,results,all_records):
        existing_ids = {a.id for a in all_records}
        for result in results:
            if result.id not in existing_ids:
                all_records.append(result)
                existing_ids.add(result.id)
        with open(storage_file, 'w') as f:
            for a in all_records:
                if a is None:
                    exit()
            json.dump([a.to_json() for a in all_records], f)
        
        return all_records

    def _load_records(self):
        if os.path.isfile(storage_file):
            with open(storage_file) as f:
                all_records = json.load(f)
        else:
            all_records = []
        
        return [AbstractObject.from_json(record) for 
                record in all_records]