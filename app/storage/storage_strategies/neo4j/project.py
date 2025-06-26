class ProjectBuilder():
    def __init__(self, graph):
        self._graph = graph
        #self._procedures = self._graph.procedure

    def get_graph(self,name):
        pass#return self._driver.project.get_graph(name)
        
    def get_projected_names(self):
        pass#return self._driver.project.names()

    def drop(self,name):
        self._graph.project.drop(name)

    def full_graph(self,directed=True):
        gn = "full_graph"
        if directed is False:
            gn += f'_undirected'
            nodes = "*"
            edges = {
                "ALL": {
                    "type": "*",
                    "orientation": "UNDIRECTED"
                }
            }
        else:
            nodes = "*"
            edges = "*"
        
        try:
            return self._graph.project.get_graph(gn)
        except ValueError:
            return self._graph.project.project(gn,nodes,edges)[0]
        
    def sub_graph(self, graph_name, node_ids=None, 
                  node_labels=None, edge_labels=None, directed=True):
        return self._graph.project.cypher(
            graph_name,
            node_ids=node_ids,
            node_labels=node_labels,
            edge_labels=edge_labels,
            directed=directed
        )


