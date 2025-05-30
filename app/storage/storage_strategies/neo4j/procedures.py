from app.storage.storage_strategies.storage_objects import StorageObject
import networkx as nx


class Procedures():
    def __init__(self, graph):
        self._graph = graph

    def get_components(self,name):
        components = {}
        res = self._graph.procedure.community_detection.wcc(name)
        for ind,record in res.iterrows():
            node = record["node"]
            component_id = int(record["componentId"])
            if component_id not in components:
                components[component_id] = []
            components[component_id].append(self._build_node(node))
        return components
    
    def all_shortest_path(self,name):
        res = self._graph.procedure.path_finding.all_shortest_path(name)
        results = []
        for index, path in res.iterrows():
            results.append((path["sourceNodeId"],path["distance"],path["targetNodeId"]))
        return results
    
    def density(self,name):
        res = self._graph.procedure.stats(name)
        n = int(res["nodeCount"].iloc[0])
        m = int(res["relationshipCount"].iloc[0])
        return m / (n * (n - 1)) if n > 1 else 0
    
    def average_local_clustering_coefficient(self,name):
        res = self._graph.procedure.community_detection.average_lcc(name)
        return res.iloc[0, 0]

    def global_clustering_coefficient(self,name):
        res = self._graph.procedure.community_detection.triangle_count(name,mode="stats")
        res = res.iloc[0]
        triangles = res["globalTriangleCount"]
        nodes = res["nodeCount"]
        # Triplets in graph ≈ nC3 = n(n-1)(n-2)/6
        triplets = (nodes * (nodes - 1) * (nodes - 2)) / 6 if nodes >= 3 else 0
        return (3.0 * triangles) / triplets if triplets > 0 else 0.0
    
    def triangles(self,name):
        res = self._graph.procedure.community_detection.triangle_count(name)
        results = []
        for index, path in res.iterrows():
            results.append((self._build_node(path["node"]),path["triangleCount"]))
        return results

    def degree_assortativity(self,name):
        data = []
        for index, path in self._graph.procedure.edge_stream(name).iterrows():
            data.append((path["sourceNodeId"],path["targetNodeId"]))
        nx_graph = self._generate_nx_graph(data)
        return nx.degree_assortativity_coefficient(nx_graph)
        
    def degree_centrality(self,name):
        results = []
        for index, path in self._graph.procedure.centrality.degree_centrality(name).iterrows():
            results.append((self._build_node(path["node"]),path["score"]))
        return results
    
    def betweenness_centrality(self,name):
        results = []
        for index, path in self._graph.procedure.centrality.betweenness_centrality(name).iterrows():
            results.append((self._build_node(path["node"]),path["score"]))
        return results
    
    def closeness_centrality(self,name):
        results = []
        for index, path in self._graph.procedure.centrality.closeness_centrality(name).iterrows():
            results.append((self._build_node(path["node"]),path["score"]))
        return results
    
    def page_rank(self,name):
        results = []
        for index, path in self._graph.procedure.centrality.page_rank(name).iterrows():
            results.append((self._build_node(path["node"]),path["score"]))
        return results

    def eigenvector_centrality(self,name):
        results = []
        for index, path in self._graph.procedure.centrality.eigenvector_centrality(name).iterrows():
            results.append((self._build_node(path["node"]),path["score"]))
        return results

    def node_similarity(self,name):
        results = []
        for index, res in self._graph.procedure.similarity.node(name).iterrows():
            results.append((self._build_node(res["node1"]),
                            self._build_node(res["node2"]),
                            res["similarity"]))
        return results
        


    def bfs(self, name, source, dest=None, max_depth=None, mode="stream"):
        res = self._graph.procedure.path_finding.bfs(name, source, dest, 
                                                     max_depth=max_depth, mode=mode)
        
        G = nx.DiGraph()

        for _, row in res.iterrows():
            path = row["path"]
            if not path.relationships:
                continue
            for rel in path.relationships:
                start = rel.start_node
                end = rel.end_node
                start_props = dict(start.items())
                end_props = dict(end.items())
                start_id = start_props.pop("identifier")
                end_id = end_props.pop("identifier")
                G.add_node(start_id, labels=list(start.labels), **start_props)
                G.add_node(end_id, labels=list(end.labels), **end_props)
                G.add_edge(start_id, end_id, type=rel.type, **dict(rel))
                print(rel.type)

        return G
    



    # -- Not reworked --
    def dfs(self, name, source, dest=None, mode="stream"):
        return self._graph.procedure.path_finding.dfs(name, source, dest, mode=mode)



    def louvain(self,name):
        return self._graph.procedure.community_detection.louvain(name)

    def label_propagation(self,name):
        return self._graph.procedure.community_detection.label_propagation(name)

    def is_connected(self, name):
        return len(set([c["componentId"] for c in 
        self._graph.procedure.community_detection.wcc(name)])) == 1

    def _build_node(self,node):
        properties = {}
        identifier = None
        for k,v in node.items():
            if k == "identifier":
                identifier = v
            else:
                properties[k] = v

        return StorageObject(identifier,list(node.labels)[0],properties)
        
    def get_inputs(self,name):
        return [s["node"] for s in 
                self._graph.procedure.centrality.degree(name,
                                        orientation="REVERSE") 
                                        if s["score"] == 0.0]
    
    def get_outputs(self,name):
        return [s["node"] for s in 
                self._graph.procedure.centrality.degree(name)
                if s["score"] == 0.0]

    def dijkstra_sp(self,name,source,target):
        return self._graph.procedure.path_finding.dijkstra_sp(name,
                                                                source,
                                                                target)
    
    def _generate_nx_graph(self,edges):
        G = nx.Graph()
        G.add_edges_from(edges)
        return G