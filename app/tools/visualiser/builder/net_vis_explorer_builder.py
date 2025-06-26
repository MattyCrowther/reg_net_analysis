
from app.tools.visualiser.builder.abstract import Builder
from app.tools.visualiser.view.view import View
from app.tools.visualiser.view.node import Node
from app.tools.visualiser.view.edge import Edge

from app.tools.visualiser.builder.builders.net_vis.interaction import InteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.interaction import VerboseInteractionBuilder
from app.tools.visualiser.builder.builders.net_vis.structural import StructuralViewBuilder

class NetVisExplorerBuilder(Builder):
    def __init__(self, storage):
        super().__init__(storage)
        self._depth = 1

    def _convert_storage_node(self,node):
        return Node(node.identifier,
                    node.object_type,
                    **node.properties)

    def _edge_conversion(self,n,v,e,**kwargs):
        return Edge(n,v,e,**kwargs)
    
    def initialise_view(self, node_id):
        self.view = View()
        visited = set()
        frontier = [(node_id, 0)]

        while frontier:
            current_id, current_depth = frontier.pop(0)
            if current_id in visited or current_depth > self._depth:
                continue

            visited.add(current_id)
            current_node = self._storage.get(identifier=current_id)
            self.view.add_node(self._convert_storage_node(current_node))

            if current_depth < self._depth:
                # Outgoing relationships
                for rel_type, rels in current_node.relationships.items():
                    for target_id in rels:
                        if target_id not in visited:
                            frontier.append((target_id, current_depth + 1))
                        self.view.add_node(self._convert_storage_node(
                            self._storage.get(identifier=target_id)))
                        self.view.add_edge(self._edge_conversion(current_id, target_id, rel_type))

                # Incoming relationships
                for source_node, edge in self._storage.get_in_relationships(current_id):
                    source_id = source_node.identifier
                    if source_id not in visited:
                        frontier.append((source_id, current_depth + 1))
                    self.view.add_node(self._convert_storage_node(source_node))
                    self.view.add_edge(self._edge_conversion(source_id, current_id, edge))

    
    def set_depth(self,depth):
        self._depth = int(depth)

    def expand_node(self,node_id):
        new_elements = []
        element = self.view.get_node(node_id)
        for e,v in self._storage.get_edges(identifier=element.id):
            v = self._convert_storage_node(v)
            if self.view.has_node(v):
                continue
            self.view.add_node(v)
            self.view.add_edge(self._edge_conversion(element.id,
                                                     v.id,e))
            new_elements.append(v)
        return element,View(new_elements)
    
    def compress_node(self,node_id):
        removed_elements = []
        for edge in list(self.view.edges(node_id)):
            self.view.remove_node(edge.v)
            removed_elements.append(edge.v)

        for node in self.view.get_isolated_nodes():
            if node.id == node_id:
                continue
            self.view.remove_node(node)
            removed_elements.append(node)
        return removed_elements
    
    def is_expanded(self,node_id):
        view_element = self.view.get_node(node_id)
        if len(list(self.view.edges(view_element))) > 0:
            return True
        return False