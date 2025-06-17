from app.tools.visualiser.visual.handlers.abstract_label import NodeLabelHandler
from app.tools.visualiser.visual.handlers.abstract_label import EdgeLabelHandler

from app.model.model import model

class NetVisNodeLabelHandler(NodeLabelHandler):
    def __init__(self,builder):
        super().__init__(builder)
        self._builder = self.name

    def name(self, elements):
        cur_view = self._graph_builder.view
        for element in elements:
            if not self._is_node(element):
                continue
            n_id = element["data"]["id"]
            node = cur_view.get_node(element["data"]["id"])
            name = node.properties.get(str(model.identifiers.external.title), n_id)
            if isinstance(name,list):
                name = name[0]
            element["data"]["label"] = name
        return elements
    
class NetVisEdgeLabelHandler(EdgeLabelHandler):
    def __init__(self,builder):
        super().__init__(builder)