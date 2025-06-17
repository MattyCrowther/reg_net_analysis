from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.tools.visualiser.view.view import View
class FullViewBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        view = View()
        for node in self._storage.get():
            view.add_node(self._node_coversion(node))
            for rt,rels in node.relationships.items():
                for rel in rels:
                    view.add_edge(self._edge_conversion(node.identifier,
                                                        rel,rt))
        return view