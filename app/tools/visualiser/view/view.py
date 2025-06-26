import networkx as nx

from app.tools.visualiser.view.edge import Edge
from app.tools.visualiser.view.node import Node

class View:
    def __init__(self, graph=None): 
        self._graph = graph if graph is not None else nx.MultiDiGraph()
        
    def __len__(self):
        return len(self._graph)

    def __eq__(self, obj):
        if isinstance(obj, self.__class__):
            return nx.is_isomorphic(self._graph, obj._graph)
        if isinstance(obj, nx.MultiDiGraph):
            return nx.is_isomorphic(self._graph, obj)
        return False

    def __iter__(self):
        for n in self._graph.nodes:
            yield n

    def _node(self,label,id,properties=None):
        if properties is None:
            props = {}
        else:
            props = properties
        
        return Node(id,label,**props)
    
    def _edge(self,n,v,e,properties=None):
        if properties is None:
            props = {}
        else:
            props = properties
        return Edge(n,v,e,**props)

    def nodes(self):
        for n,data in self._graph.nodes(data=True):
            props = data.copy()
            label = props.pop("type")
            yield self._node(label,n,properties=props)

    def edges(self,n=None):
        if isinstance(n,Node):
            n = n.id

        for n,v,e,d in self._graph.edges(n,keys=True,data=True):
            props = self._graph.nodes[n].copy()
            o_type = props.pop("type")
            n = self._node(o_type,n,properties=props)

            props = self._graph.nodes[v].copy()
            o_type = props.pop("type")
            v = self._node(o_type,v,properties=props)
            yield self._edge(n,v,e,properties=d)
        
    def get_edge_type(self,n,v):
        return list(self._graph.get_edge_data(n,v).keys())[0]

    def get_node(self,n=None):
        if n is None:
            return list(self.nodes())
        data = self._graph.nodes[n]
        props = data.copy()
        o_type = props.pop("type")
        return self._node(o_type,id=n,properties=props)

    def in_edges(self, node=None):
        for n,v,e,d in self._graph.in_edges(node,keys=True,data=True):
            props = self._graph.nodes[n].copy()
            o_type = props["key"]
            del props["key"]
            n = self._node(o_type,id=n,properties=props)

            props = self._graph.nodes[v].copy()
            o_type = props["key"]
            del props["key"]
            v = self._node(o_type,id=v,properties=props)
            yield self._edge(n,v,e,properties=d)

    def has_edge(self,edge):
        return self._graph.has_edge(edge.n,
                                    edge.v,
                                    key=edge.type)
    
    def has_node(self,node):
        if isinstance(node,Node):
            node = node.id
        return self._graph.has_node(node)
    
    def add_edge(self, edge):
        self._graph.add_edge(edge.n,
                             edge.v,
                             edge.type,
                             **edge.properties)

    def add_node(self, node):
        self._graph.add_node(node.id,
                             type=node.type,
                             **node.properties)
        
    def remove_node(self,node):
        self._graph.remove_node(node.id)

    def get_isolated_nodes(self):
        isolated_nodes = list(nx.isolates(self._graph))
        return [self.get_node(n) for n in isolated_nodes]
