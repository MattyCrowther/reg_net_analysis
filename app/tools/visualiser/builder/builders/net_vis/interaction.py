from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.model.model import model

nv_interaction = model.identifiers.objects.interaction
class InteractionBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        i_classes = [str(n) for n in 
                     model.get_all_subclasses(nv_interaction)]
        nodes = []
        for i in self._storage.get(i_classes):
            rel_ids = [rel for sublist in 
                            i.relationships.values() 
                            for rel in sublist]
            nodes.append(i)
            nodes += self._storage.get(identifier=rel_ids)

        # Note:: Could be good to get the edges I/O direction 
        # so inputs into the interaction node etc. Genetta did it i think.
        return self._new_view(nodes)