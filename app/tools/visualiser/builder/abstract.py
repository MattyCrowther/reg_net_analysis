from app.tools.visualiser.view.view import View

class Builder:
    def __init__(self, storage):
        self._storage = storage
        self.view = View()

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



