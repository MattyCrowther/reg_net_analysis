import os
import re

from rdflib import RDFS
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import Graph
from rdflib import OWL
from rdflib import Literal

import networkx as nx

from app.model.identifiers import produce_identifiers

model_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"model.xml")
'''
Note for future self. The Semantic modelling here is a little 
half arsed. It was enough to get something graph ready and relatively tractable.
'''
class ModelGraph:
    def __init__(self):
        self._graph = _load_graph()
        self.identifiers = produce_identifiers(self)
        
    def __iter__(self):
        for n in self._graph.nodes:
            yield n

    @property
    def nodes(self):
        return self._graph.nodes

    @property
    def edges(self):
        return self._graph.edges

    def get_class(self,equivalent):
        '''
        Given an equivalent Symbol, returns the standard class.
        '''
        equivalent = Literal(equivalent)
        res = self.search((None,OWL.hasValue,Literal(equivalent)),lazy=True)
        assert(len(res) == 3)
        s,o,p = res
        while p != OWL.equivalentClass:
            s,o,p = self.search((None,None,s),lazy=True)
        return s[1]["key"]
    
    def get_predicate(self,domain_type,equivalent):
        '''
        Given an equivalent symbol, return the 
        predicate attached to the standard class.
        '''
        equivalent = Literal(equivalent)
        for s,o,p in self.search((None,OWL.equivalentProperty,Literal(equivalent))):
            res = self.search((s[0],RDFS.domain,None),lazy=True)
            assert(len(res) == 3)
            res = self.search((res[1][0],OWL.unionOf,None),lazy=True)
            
            rest = None
            res = res[1][0]
            while rest != RDF.nil:
                domain = self.search((res,RDF.first,None),lazy=True)
                domain = domain[1][1]["key"]
                if domain == domain_type:
                    return s[1]["key"]
                rest = self.search((res,RDF.rest,None),lazy=True)
                res = rest[1][0]
                rest = rest[1][1]["key"]
                
        else:
            raise ValueError(equivalent)

    def is_relationship(self,predicate):
        cls_code = self._get_class_code(predicate)
        if len(self.search((cls_code,RDF.type,OWL.ObjectProperty),lazy=True)) == 0:
            return False
        return True

    def _get_class_code(self,label):
        if not isinstance(label,list):
            label = [label]
        label = [str(l) for l in label]
        for n,data in self.nodes(data=True):
            if str(data["key"]) in label:
                return n
        raise ValueError(f'{label} is not in graph.')
    
    def search(self, pattern, lazy=False,label_key="key"):
        matches = []
        s, p, o = pattern
        if not isinstance(s, (list, set, tuple)):
            s = [s]
        if p and not isinstance(p, (list, set, tuple)):
            p = [p]
        if o and not isinstance(o, (list, set, tuple)):
            o = [o]
        for subject in s:
            subject = [subject]
            for ns in subject:
                for n, v, k in self.edges(ns, keys=True):
                    if not p or k in p:
                        n_data = self.nodes[n]
                        v_data = self.nodes[v]
                        if not o or v_data[label_key] in o or v in o:
                            if lazy:
                                return ([n, n_data], [v, v_data], k)
                            matches.append(([n, n_data], [v, v_data], k))
        return matches

def _load_graph():
    g = Graph()
    g.parse(model_fn)
    nx_graph = nx.MultiDiGraph()
    node_count = 1
    node_map = {}
    def _add_node(entity,node_count):
        if entity in node_map.keys():
            n_key = node_map[entity]
        else:
            n_key = node_count
            node_map[entity] = n_key
            node_count += 1
        nx_graph.add_node(n_key, key=entity)
        return n_key,node_count

    for s,p,o in g.triples((None,None,None)):
        n,node_count = _add_node(s,node_count)
        v,node_count = _add_node(o,node_count)
        nx_graph.add_edge(n,v,key=p,weight=1)

    return nx_graph

model = ModelGraph()