import math
from app.tools.visualiser.visual.handlers.abstract_handler import HandlerABC

class SizeHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Node Size")
        self._standard_node_size = 20
        self._builder = self.default_builder()
    
    def default_builder(self):
        return self.standard
    
    def standard(self, elements):
        for element in elements:
            # Its an edge
            if not self._is_node(element):
                continue
            element["data"]["size"] = self._standard_node_size
        return elements

    def type(self,elements):
        cur_view = self._graph_builder.view
        for element in elements:
            # Its an edge
            if not self._is_node(element):
                continue
            node = cur_view.get_element(element["data"]["id"])
            node_type = node.object_type
            if node_type is None:
                element["data"]["size"] = self._standard_node_size/2
            else:
                element["data"]["size"] = self._standard_node_size
        return elements

    def centrality(self, elements):
        cur_view = self._graph_builder.view
        
        node_degrees = {}
        for elem in elements:
            if not self._is_node(elem):
                continue
            node = cur_view.get_element(elem["data"]["id"])
            count = 0
            for rels in node.relationships.values():
                count += len(rels)
            node_degrees[node.identifier] = count
        
        max_degree = max(node_degrees.values(), default=1)
        
        min_size = self._standard_node_size / 2
        max_size = 100
        
        for elem in elements:
            if not self._is_node(elem):
                continue
            
            node_id = elem["data"]["id"]
            degree = node_degrees[node_id]
            
            if max_degree > 1:
                log_scaled_size = int(
                    min_size 
                    + (max_size - min_size) 
                    * (math.log1p(degree) / math.log1p(max_degree))
                )
            else:
                log_scaled_size = int(min_size)
            elem["data"]["size"] = max(min_size, min(log_scaled_size, max_size))
    
        return elements
