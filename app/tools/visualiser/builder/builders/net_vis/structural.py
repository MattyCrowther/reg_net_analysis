from app.tools.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.model.model import model

nv_has_part = model.identifiers.predicates.has_part
class StructuralViewBuilder(AbstractViewBuilder):
    def __init__(self,storage):
        super().__init__(storage)
        
    def build(self):
        results = []
        for n,v,e in self._storage.get_edges(edge_type=nv_has_part):
            n.add_relationship(e.type,v.identifier)
            if n in results:
                # replace the old `n` with the updated one
                idx = results.index(n)
                results[idx] = n
            results.append(n)
            if v not in results:
                results.append(v)
        return self._new_view(results)