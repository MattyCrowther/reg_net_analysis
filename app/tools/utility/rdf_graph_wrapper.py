import rdflib
from app.model.model import model

rdf_type = rdflib.RDF.type
class RDFGraphWrapper:
    def __init__(self, graph = None):
        if isinstance(graph,rdflib.Graph):
            self._graph = graph
        else:
            self._graph = rdflib.Graph()
            if graph is not None:
                self._graph.parse(graph)

    def __iter__(self):
        for x in self._graph:
            yield x
            
    def __len__(self):
        return len(self._graph)
        
    def get_objects(self):
        return [s[0] for s in self.search((None,rdf_type,None))]
    
    def get_object(self,identifier):
        object_type = None
        properties = {}
        relationships = {}
        for _,p,o in self.search((identifier,None,None)):
            if p == rdf_type:
                object_type = o
                continue
            if isinstance(o,rdflib.Literal):
                if p not in properties:
                    properties[p] = []
                properties[p].append(o)
            elif model.is_relationship(p):
                if p not in relationships:
                    relationships[p] = []
                relationships[p].append(o)
            else:
                if p not in properties:
                    properties[p] = []
                properties[p].append(o)

        v = GraphObject(object_type,identifier,properties,relationships)
        return v
            

    def search(self,pattern,lazy=False):
        if lazy:
            for res in self._graph.triples(pattern):
                return res
            return None
        else:
            results = []
            for res in self._graph.triples(pattern):
                results.append(res)
            return results


    def serialize(self,filename,format):
        return self._graph.serialize(filename,format)

class GraphObject():
    def __init__(self,type,identifier,properties,relationships):
        self._type = type
        self._properties = properties
        self._relationships = relationships
        self._id = identifier


    @property
    def id(self):
        return self._id
    
    @property
    def type(self):
        return self._type
    
    @property
    def properties(self):
        return self._properties
    
    @property
    def relationships(self):
        return self._relationships
