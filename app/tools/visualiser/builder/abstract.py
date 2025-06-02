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


    def get_view_elements(self,sub_view=None,initial_edge_index=0):
        edge_index = initial_edge_index
        if sub_view is None:
            sub_view = self.view
        
        nodes = []
        edges = []
        for element in sub_view:
            node = self._build_node(element)
            nodes.append(node)
            for _,rels in element.relationships.items():
                for rel in rels:
                    if sub_view.get_element(rel) is None:
                        continue
                    edge = self._build_edge(element.identifier,
                                            rel,edge_index)
                    edge_index += 1
                    edges.append(edge)
        return nodes+edges

    def _build_node(self, element):
        class_str = f'top-center'
        node = {'data': {'id': str(element.identifier)},
                'classes': class_str}
        return node

    def _build_edge(self, n,v,e):
        edge = {'data': {'source': str(n), 
                         'target': str(v),
                         "id" : str(e)},
                'classes': f'center-right'}
        return edge



