from app.tools.visualiser.visual.handlers.abstract_handler import HandlerABC

class NodeLabelHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Node Labels")
        self._builder = self.default_builder()

    def default_builder(self):
        return self.uri

    def none(self, elements):
        for element in elements:
            if not self._is_node(element):
                continue
            element["data"]["label"] = ""
        return elements

    def uri(self, elements):
        for element in elements:
            if not self._is_node(element):
                continue
            n_id = element["data"]["id"]
            element["data"]["label"] = n_id
        return elements
    
    def adjacency(self,elements):
        cur_view = self._graph_builder.view
        for element in elements:
            # Its an edge
            if not self._is_node(element):
                continue
            node = cur_view.get_node(element["data"]["id"])
            count = len(list(cur_view.edges(node)))
            element["data"]["label"] = f"{str(count)}"
        return elements

    def class_type(self,elements):
        cur_view = self._graph_builder.view
        for element in elements:
            # Its an edge
            if not self._is_node(element):
                continue
            node = cur_view.get_node(element["data"]["id"])
            n_type = node.type
            if n_type is None:
                class_type = "unknown"
            else:
                class_type = n_type
            element["data"]["label"] = class_type
        return elements
    
    def _is_node(self,element):
        if "source" in element["data"] and "target" in element["data"]:
            return False
        return True
        
class EdgeLabelHandler(HandlerABC):
    def __init__(self, graph_builder):
        super().__init__(graph_builder,"Edge Labels")
        self._builder = self.default_builder()

    def default_builder(self):
        return self.none
    
    def none(self,elements):
        for element in elements:
            # Its an edge
            if not self._is_edge(element):
                continue
            element["data"]["label"] = ""
        return elements

    def relationship_type(self,elements):
        cur_view = self._graph_builder.view
        for element in elements:
            # Its an edge
            if not self._is_edge(element):
                continue
            source = element["data"]["source"]
            target = element["data"]["target"]
            edge_type = cur_view.get_edge_type(source,target)
            if edge_type is None:
                rel_type = "unknown"
            else:
                rel_type = edge_type
            element["data"]["label"] = rel_type
        return elements
    
    def _is_edge(self,element):
        if "source" in element["data"] and "target" in element["data"]:
            return True
        return False