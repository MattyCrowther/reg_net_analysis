
from app.tools.visualiser.builder.abstract import Builder
from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.tools.visualiser.builder.builders.full import FullViewBuilder
from app.tools.visualiser.builder.builders.net_vis.interaction import InteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.interaction import VerboseInteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.structural import StructuralViewBuilder

class NetVisViewBuilder(Builder):
    def __init__(self, storage):
        super().__init__(storage)
        self._view_builder = StructuralViewBuilder(self._storage)

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