from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.tools.visualiser.view.view import View
from app.model.model import model

nv_has_part = model.identifiers.predicates.has_part
class StructuralViewBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        view = View()
        for n,v,e in self._storage.get_edges(edge_type=nv_has_part):
            view.add_node(self._node_coversion(n))
            view.add_node(self._node_coversion(v))
            view.add_edge(self._edge_conversion(n.identifier,
                                                v.identifier,
                                                e.type))
        return view