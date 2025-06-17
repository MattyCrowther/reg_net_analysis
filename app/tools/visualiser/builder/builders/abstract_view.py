from app.tools.visualiser.view.edge import Edge
from app.tools.visualiser.view.node import Node
class AbstractViewBuilder():
    def __init__(self,storage):
        self._storage = storage


    def _node_coversion(self,node):
        conv_node = Node(node.identifier,
                         node.object_type,
                         **node.properties)
        return conv_node
    
    def _edge_conversion(self,n,v,e,**kwargs):
        return Edge(n,v,e,**kwargs)