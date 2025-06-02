#from net_vis_register.topic_utilities import topic_utilities
#from net_vis_storage.storage_strategies.storage_objects import StorageObject
from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder

class FullViewBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        nodes = self._storage.get()
        return self._new_view(nodes)