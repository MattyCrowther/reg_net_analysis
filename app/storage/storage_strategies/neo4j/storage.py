from app.storage.storage_strategies.neo4j.interface import Neo4jInterface
from app.storage.storage_strategies.abstract_storage import AbstractStorage
from app.storage.storage_strategies.storage_objects import StorageObject
from app.storage.storage_strategies.neo4j.project import ProjectBuilder
from app.storage.storage_strategies.neo4j.procedures import Procedures

class Neo4jStorage(AbstractStorage):
    def __init__(self, uri, username=None,password=None):
        super().__init__()
        self._interface = Neo4jInterface(uri,username=username,
                                         password=password)
        self.project = ProjectBuilder(self._interface)
        self.procedure = Procedures(self._interface)


    def drop(self):
        return self._interface.drop()
    
    def add_rdf_graph(self,graph):
        existing_object_ids = self.get_ids()
        for object in graph.get_objects():
            object = graph.get_object(object)
            if str(object.id) in existing_object_ids:
                print(f'Updating: {object.id}')
                self.update_entity(object.id,
                            object.type,
                            object.relationships,
                            object.properties)
            else:
                print(f'Adding: {object.type},{object.id}')
                self.add_entity(object.type,
                         object.id,
                         object.relationships,
                         object.properties)
            existing_object_ids.append(str(object.id))

    def get_ids(self):
        ids = self._interface.get_property("identifier")
        return list(set(item for sublist in ids for item in sublist))

    def add_entity(self, label, identifier, relationships, properties):
        self._interface.add_node(label,identifier,properties) 
        for rel_key, objs in relationships.items():
            for linked_obj in objs:
                self._interface.add_relationship(identifier,linked_obj,rel_key)
    
    def add_relationship(self,entity1, entity2, relationship_type):
        self._interface.add_relationship(entity1.identifier,
                                         entity2.identifier,
                                         relationship_type.value)

    def update_entity(self,identifier,type,
                      relationships,props):
        # Remove eventually.
        entity = self.get(identifier=identifier)
        if entity is not None:
            assert(entity.object_type == str(type))
        
        self._interface.update_node(identifier,type,props)
        for rel_key, objs in relationships.items():
            for linked_obj in objs:
                self._interface.add_relationship(identifier,linked_obj,rel_key)

    def get(self, object_type=None, identifier=None,**kwargs):
        results = []
        if (isinstance(object_type,(list,set,tuple)) or 
            isinstance(identifier,(list,set,tuple))):
            nodes = self._interface.get_nodes(object_type,
                                              identifier,
                                              get_relationships=True)
        else:
            nodes = self._interface.get_node(label = object_type,
                                            identifier=identifier,
                                            get_relationships=True,
                                            **kwargs)
        if identifier is not None:
            if len(nodes) == 0:
                return None
            if len(nodes) == 1:
                return self._create_object(nodes[0][0],nodes[0][1])
        
        for node,rels in nodes:
            results.append(self._create_object(node,rels))

        return results
    
    def get_edges(self,identifier=None,
                  edge_type=None):
        # Mainly for case where node is taken without rels (namely GDS stuff)
        results = []
        if identifier is not None:
            for _,e,v in self._interface.get_relationships(identifier):
                results.append((e.type,self._create_object(v)))
        if edge_type is not None:
            for n,e,v in self._interface.get_relationship(relationship_type=edge_type,
                                                      return_nodes=True):
                results.append((self._create_object(n),
                                self._create_object(v),e))
        return results

    def node_count(self):
        return self._interface.node_count()
    
    def edge_count(self):
        return self._interface.edge_count()
    
    def get_isolated_nodes(self):
        return [self._create_object(o) for o in self._interface.get_isolated_nodes()]
    
    def get_degree_distribution(self):
        return self._interface.get_degree_distribution()
    
    def get_reciprocity(self):
        bidirectional = self._interface.get_bidirectional()
        total = self.edge_count()

        if total == 0:
            return 0.0
        return (2 * bidirectional) / total

    def _create_object(self,node,rels=None):
        # Its an integration thing. When rel adds node before node data
        if len(node.labels) == 0:
            return None

        assert(len(node.labels) == 1)
        entity_type = list(node.labels)[0]
        properties = dict(node.items())
        assert("identifier" in properties)
        identifier = properties.pop("identifier")
        
        relationships = {}
        if rels is not None:
            for rel in rels:
                edge = rel["r"]
                vertex = rel["v"]
                if edge is None:
                    continue
                if edge not in relationships:
                    relationships[edge] = []
                relationships[edge].append(vertex)

        return StorageObject(identifier,entity_type,properties,relationships)