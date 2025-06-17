
from app.tools.visualiser.builder.abstract import Builder
from app.tools.visualiser.view.view import View
from app.tools.visualiser.builder.builders.net_vis.interaction import InteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.interaction import VerboseInteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.structural import StructuralViewBuilder
class NetVisBuilder(Builder):
    def __init__(self, storage):
        super().__init__(storage)
        self._view_builder = StructuralViewBuilder(self._storage)

    def expand_node(self,node_id):
        new_elements = []
        element = self.view.get_element(node_id)
        for rel_type,rels in element.relationships.items():
            for rel in rels:
                if self.view.has_element(rel):
                    continue
                to_add_element = self._storage.get(identifier=rel)
                self.view.add_element(to_add_element)
                new_elements.append(to_add_element)
        return View([element]+new_elements)
    

    def compress_node(self,node_id):
        removed_elements = []
        element = self.view.get_element(node_id)
        for rel_type,rels in element.relationships.items():
            for rel in rels:
                if not self.view.has_element(rel):
                    continue
                self.view.remove_element(rel)
                removed_elements.append(rel)
        return removed_elements
    
    def is_expanded(self,node_id):
        view_element = self.view.get_element(node_id)
        for rel_type,rels in view_element.relationships.items():
            for rel in rels:
                if not self.view.has_element(rel):
                    return False

        return True