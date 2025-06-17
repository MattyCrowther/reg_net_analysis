from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.model.model import model
from app.tools.visualiser.view.view import View

nv_interaction = model.identifiers.objects.interaction
nv_input = model.identifiers.objects.input
class VerboseInteractionBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        v = View()
        i_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_interaction)]
        
        for i in self._storage.get(i_classes):
            v.add_node(self._node_coversion(i))
            rel_ids = [rel for sublist in 
                            i.relationships.values() 
                            for rel in sublist]

            node_rels = self._storage.get(identifier=rel_ids)
            for rel_type,rels in i.relationships.items():
                rel_dir = model.get_interaction_direction(rel_type)
                for rel in rels:
                    for nrel in node_rels:
                        if nrel.identifier == rel:
                            if rel_dir == nv_input:
                                v.add_edge(self._edge_conversion(nrel.identifier,
                                                                 i.identifier,
                                                                 rel_type))
                            else:
                                v.add_edge(self._edge_conversion(i.identifier,
                                                                 nrel.identifier,
                                                                 rel_type))
                            v.add_node(self._node_coversion(nrel))
                            break
        return v

class InteractionBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        v = View()
        i_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_interaction)]
        
        for i in self._storage.get(i_classes):
            rel_ids = [rel for sublist in 
                            i.relationships.values() 
                            for rel in sublist]

            node_rels = self._storage.get(identifier=rel_ids)
            inputs = []
            outputs = []
            for rel_type,rels in i.relationships.items():
                rel_dir = model.get_interaction_direction(rel_type)
                for rel in rels:
                    for nrel in node_rels:
                        if nrel.identifier == rel:
                            if rel_dir == nv_input:
                                inputs.append(self._node_coversion(nrel))
                            else:
                                outputs.append(self._node_coversion(nrel))
                            break

            for inp in inputs:
                v.add_node(inp)
                for out in outputs:
                    if out not in v:
                        v.add_node(out)
                    v.add_edge(self._edge_conversion(inp.id,
                                                     out.id,
                                                     i.object_type[0]))
        return v