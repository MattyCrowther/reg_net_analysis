from app.tools.visualiser.view.view import View
from app.tools.visualiser.builder.builders.full import FullViewBuilder
from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
class Builder:
    def __init__(self, storage):
        self._storage = storage
        self.view = View()
        self._view_builder = FullViewBuilder(self._storage)

    def get_builder_options(self):
        return [{"builder" : self.__class__.__name__,
                 "name" : "Graph Builder",
                 "default" : self._view_builder.__class__.__name__,
                 "options": [cls.__name__ for cls in 
                             AbstractViewBuilder.__subclasses__()]}]
        

    def set_view(self,view_builder=None):
        if view_builder is not None:
            for builder_class in AbstractViewBuilder.__subclasses__():
                if builder_class.__name__ == view_builder:
                    self._view_builder = builder_class(self._storage)
                    break
            else:
                raise ValueError(f"Invalid view name: {view_builder}")
        
        self.view = self._view_builder.build()


    def get_view_elements(self,sub_view=None):
        if sub_view is None:
            sub_view = self.view
        
        nodes = []
        edges = []
        for node in sub_view.nodes():
            node = self._build_node(node)
            nodes.append(node)
        
        for edge in sub_view.edges():
            edge = self._build_edge(edge)
            edges.append(edge)

        return nodes+edges

    def _build_node(self, node):
        class_str = f'top-center'
        node = {'data': {'id': str(node.id)},
                'classes': class_str}
        return node

    def _build_edge(self, edge):
        if edge.n == edge.v:
            raise ValueError(edge)
        edge = {'data': {'source': str(edge.n), 
                         'target': str(edge.v),
                         "id" : f'{str(edge.id)}'},
                'classes': f'center-right'}
        return edge



