from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.storage.storage_strategies.file_system.storage import FileSystemStorage
storage_mechanisms = {"file": FileSystemStorage,
                      "neo4j" : Neo4jStorage}

class StorageHandler():
    def __init__(self, code,*args,**kwargs):
        if code not in storage_mechanisms:
            raise ValueError(f"{code} not in {list(storage_mechanisms.keys())}")
        
        storage = storage_mechanisms[code](*args,**kwargs)
        self._storage = storage

    @staticmethod
    def get_storage_codes():
        return list(storage_mechanisms.keys())

    def add_rdf_graph(self,graph):
        existing_object_ids = self._storage.get_ids()
        for object in graph.get_objects():
            object = graph.get_object(object)
            if str(object.id) in existing_object_ids:
                print(f'Updating: {object.id}')
                self.update(object.id,
                            object.type,
                            object.relationships,
                            object.properties)
            else:
                print(f'Adding: {object.type},{object.id}')
                self.add(object.type,
                         object.id,
                         object.relationships,
                         object.properties)
            existing_object_ids.append(str(object.id))

    def add(self,label,identifier,relationships,properties):
        return self._storage.add_entity(label,identifier,
                                        relationships,properties)
    
    def update(self,identifier,type,relationships,properties):
        return self._storage.update_entity(identifier,type,
                                           relationships,properties)

    def get(self,identifier=None,label=None,**kwargs):
        return self._storage.get(label,identifier,**kwargs)

    def remove(self,identifier):
        self._storage.remove(identifier)