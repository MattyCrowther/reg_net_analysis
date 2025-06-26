from app.storage.storage_strategies.storage_objects import StorageObject

class Call:
    def __init__(self, procedure, name, mode=None):
        self.procedure = procedure
        self.name = name
        self.mode = mode

class StringBuilder:
    def __init__(self):
        self._matches = {}
        self._wheres = []
        self._parameters = {}
        self._arguments = []
        self._call = None
        self._yields = []
        self._returns = []

    def MATCH(self, name, where):
        if not isinstance(where, list):
            where = [where]
        self._matches[name] = where
        return self

    def CALL(self, procedure, name, mode=None):
        self._call = Call(procedure, name, mode)
        return self

    def PARAMETER(self, key, value):
        self._parameters[key] = value
        return self

    def ARGUMENT(self, argument):
        self._arguments.append(argument)
        return self

    def YIELD(self, yields):
        if not isinstance(yields, list):
            yields = [yields]
        self._yields += yields
        return self

    def RETURN(self, val):
        if not isinstance(val, list):
            val = [val]
        self._returns += val
        return self

    def BUILD(self):
        f_str = ""

        # MATCH
        for name, match in self._matches.items():
            f_str += f"MATCH ({name}) "
            if match:
                f_str += "WHERE "
                for index, i in enumerate(match):    
                    if i is not None:
                        if isinstance(i,StorageObject):
                            f_str += f'{name}.identifier = "{i.identifier}" '
                        else:
                            f_str += f'{name}:`{i}` '
                        if index < len(match) - 1:
                            f_str += " OR "

        # CALL
        if self._call:
            mode = f".{self._call.mode}" if self._call.mode else ""
            f_str += f"CALL {self._call.procedure}{mode}('{self._call.name}'"

            # Add arguments
            if self._arguments:
                for arg in self._arguments:
                    f_str += f", '{arg}'"

            # Add parameters
            if self._parameters:
                f_str += ", {"
                param_strs = []
                for k, v in self._parameters.items():
                    if isinstance(v, str) and v not in self._matches.keys():
                        v = f'"{v}"'
                    param_strs.append(f'{k}: {v}')
                f_str += ", ".join(param_strs)
                f_str += "}"

            f_str += ") "

        # YIELD
        if self._yields:
            f_str += f"YIELD {', '.join(self._yields)} "

        # RETURN
        if self._returns:
            f_str += f"RETURN {', '.join(self._returns)} "

        return f_str.strip()


class GDSQueryBuilder:
    def __init__(self):
        pass
        

    def cypher_project(self, node_ids=None, node_labels=None, edge_labels=None, directed=True):
        # Node filter setup
        node_filters = []

        if node_ids:
            if isinstance(node_ids, str):
                node_ids = [node_ids]
            id_list = "[" + ", ".join(f'"{nid}"' for nid in node_ids) + "]"
            node_filters.append(f"n.identifier IN {id_list}")

        if node_labels:
            if isinstance(node_labels, str):
                node_labels = [node_labels]
            label_filter = " OR ".join(f'"{label}" IN labels(n)' for label in node_labels)
            node_filters.append(f"({label_filter})")

        node_where = " AND ".join(node_filters)
        if node_where:
            node_where = " AND " + node_where

        # Relationship filter
        if edge_labels:
            if isinstance(edge_labels, str):
                edge_labels = [edge_labels]
            rel_list = "[" + ", ".join(f'"{t}"' for t in edge_labels) + "]"
            edge_filter = f"type(r) IN {rel_list}"
        else:
            edge_filter = None

        rel_arrow = "->" if directed else "-"

        # Final node and rel queries
        node_query = f"""
        MATCH (n)
        WHERE (
            EXISTS {{
                MATCH (n)-[r]{rel_arrow}() {f"WHERE {edge_filter}" if edge_filter else ""}
            }} OR EXISTS {{
                MATCH ()-[r]{rel_arrow}(n) {f"WHERE {edge_filter}" if edge_filter else ""}
            }}
        ){node_where}
        RETURN id(n) AS id
        """

        rel_query = f"""
        MATCH (a)-[r]{rel_arrow}(b)
        {f"WHERE {edge_filter}" if edge_filter else ""}
        RETURN id(a) AS source, id(b) AS target, type(r) AS type
        """

        return node_query.strip(), rel_query.strip()

    def mutate(self,name,types,mutate_type,node_labels=None):
        sb = StringBuilder()
        sb.CALL("gds.beta.collapsePath",name,"mutate")
        sb.PARAMETER("pathTemplates",types)
        sb.PARAMETER("mutateRelationshipType",mutate_type)
        sb.PARAMETER("allowSelfLoops",False)
        if node_labels:
            sb.PARAMETER("nodeLabels",node_labels)
        sb.YIELD("relationshipsWritten")
        return sb.BUILD()

    def stats(self,name):
        sb = StringBuilder()
        sb.CALL("gds.graph.list",name)
        sb.YIELD(["nodeCount", "relationshipCount"])
        sb.RETURN(["nodeCount", "relationshipCount"])
        return sb.BUILD()
    
    def edge_stream(self,name):
        sb = StringBuilder()
        sb.CALL("gds.graph.relationships.stream",name)
        sb.YIELD(["sourceNodeId", "targetNodeId","relationshipType"])
        sb.RETURN(["sourceNodeId", "targetNodeId","relationshipType"])
        return sb.BUILD()
    
    def node_stream(self,name):
        sb = StringBuilder()
        sb.CALL("gds.graph.nodeProperty.stream",name)
        sb.ARGUMENT("identifier")
        sb.YIELD(["nodeId"])
        sb.RETURN(["gds.util.asNode(nodeId)"])
        return sb.BUILD()
    
    def page_rank(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.pageRank",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def article_rank(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.articleRank",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def eigenvector_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.eigenvector",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def betweenness_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.betweenness",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def degree_centrality(self,name,mode="stream",orientation="NATURAL"):
        sb = StringBuilder()
        sb.CALL("gds.degree",name,mode)
        sb.PARAMETER("orientation",orientation)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def closeness_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.closeness",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def node_2_vec(self,name,mode="write",**kwargs):
        sb = StringBuilder()
        sb.CALL("gds.node2vec",name,mode)
        for k,v in kwargs.items():
            sb.PARAMETER(k,v)
        if mode == "stream":
             sb.YIELD(["nodeId,embedding"])
        elif mode == "write":
            if "writeProperty" not in kwargs: 
                sb.PARAMETER("writeProperty",
                             'embedding')
            sb.YIELD(["nodeCount"])
        return sb.BUILD()
    

    def harmonic_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.closeness.harmonic",name,mode)
        sb.YIELD(["nodeId","centrality"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "centrality"])
        return sb.BUILD()

    def hits(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.hits",name,mode)
        sb.PARAMETER("hitsIterations", 20)
        sb.YIELD(["nodeId","values"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "values"])
        return sb.BUILD()

    def celf_influence_maximization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.influenceMaximization.celf",name,mode)
        sb.PARAMETER("seedSetSize", 3)
        sb.YIELD(["nodeId","spread"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "spread"])
        return sb.BUILD()

    def greedy_influence_maximization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.influenceMaximization.greedy",name,mode)
        sb.PARAMETER("seedSetSize", 3)
        sb.YIELD(["nodeId","spread"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "spread"])
        return sb.BUILD()

    def louvain(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.louvain",name,mode)
        sb.YIELD(["nodeId","communityId","intermediateCommunityIds"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId","intermediateCommunityIds"])
        return sb.BUILD()

    def label_propagation(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.labelPropagation",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()
    
    def wcc(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.wcc",name,mode)
        sb.YIELD(["nodeId","componentId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "componentId"])
        return sb.BUILD()

    def triangle_count(self,name,mode="stream"):
        if mode == "stream":
            sb = StringBuilder()
            sb.CALL("gds.triangleCount",name,mode)
            sb.YIELD(["nodeId","triangleCount"])
            sb.RETURN(["gds.util.asNode(nodeId) AS node", "triangleCount"])
            return sb.BUILD()
        elif mode == "stats":
            sb = StringBuilder()
            sb.CALL("gds.triangleCount",name,mode)
            sb.YIELD(["globalTriangleCount", "nodeCount"])
            sb.RETURN(["globalTriangleCount", "nodeCount"])
            return sb.BUILD()

    def average_lcc(self,name):
        sb = StringBuilder()
        sb.CALL("gds.localClusteringCoefficient",name,"stats")
        sb.YIELD(["averageClusteringCoefficient"])
        sb.RETURN(["averageClusteringCoefficient"])
        return sb.BUILD()


    def local_clustering_coefficient(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.localClusteringCoefficient",name,mode)
        sb.YIELD(["nodeId","localClusteringCoefficient"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "localClusteringCoefficient"])
        return sb.BUILD()

    def k1coloring(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.beta.k1coloring",name,mode)
        sb.YIELD(["nodeId","color"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "color"])
        return sb.BUILD()

    def modularity_optimization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.beta.modularityOptimization",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()
    
    def scc(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.scc",name,mode)
        sb.YIELD(["nodeId","componentId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "componentId"])
        return sb.BUILD()

    def sllpa(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.sllpa",name,mode)
        sb.PARAMETER("maxIterations", 100)
        sb.YIELD(["nodeId","values"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "values.communityIds AS communityIds"])
        return sb.BUILD()
    
    def maxkcut(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.maxkcut",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()

    def node_similarity(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.nodeSimilarity",name,mode)
        sb.YIELD(["node1", "node2", "similarity"])
        sb.RETURN(["gds.util.asNode(node1) AS node1", 
                   "gds.util.asNode(node2) AS node2", 
                   "similarity"])
        return sb.BUILD()

    def knn(self,name,node_properties,mode="stream"):
        if not isinstance(node_properties,list):
            node_properties = [node_properties]
        sb = StringBuilder()
        sb.CALL("gds.knn",name,mode)
        sb.PARAMETER("nodeProperties",str(node_properties))
        sb.PARAMETER("topK",1)
        sb.PARAMETER("randomSeed",1337)
        sb.PARAMETER("concurrency",1)
        sb.PARAMETER("sampleRate",1.0)
        sb.PARAMETER("deltaThreshold",0.0)
        sb.YIELD(["node1", "node2", "similarity"])
        sb.RETURN(["gds.util.asNode(node1) AS node1", 
                   "gds.util.asNode(node2) AS node2", "similarity"])
        return sb.BUILD()

    def all_shortest_paths(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.allShortestPaths",name,mode)
        sb.YIELD(["sourceNodeId", "targetNodeId", "distance"])
        sb.RETURN(["sourceNodeId","targetNodeId","distance"])
        return sb.BUILD()

    def dijkstra_all_shortest_paths(self,name,source,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.CALL("gds.allShortestPaths.dijkstra",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def dijkstra_shortest_path(self,name,source,dest,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.dijkstra",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def astar_shortest_path(self,name,source,dest,latitude_property,
                            longitude_property,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.astar",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.PARAMETER("latitudeProperty",latitude_property)
        sb.PARAMETER("longitudeProperty",longitude_property)
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def yens_shortest_path(self,name,source,dest,k,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.yens",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.PARAMETER("k",k)
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def dfs(self,name,source,dest=None,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        if dest is not None:
            sb.MATCH("dest",dest)
        sb.CALL("gds.dfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        if dest is not None:
            sb.PARAMETER("targetNodes","dest")
        sb.YIELD("path")
        sb.RETURN("path")
        return sb.BUILD()

    def bfs(self,name,source,dest=None,max_depth=None,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        if dest is not None:
            sb.MATCH("dest",dest)
        sb.CALL("gds.bfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        if dest is not None:
            sb.PARAMETER("targetNodes","dest")
        if max_depth is not None:
            sb.PARAMETER("maxDepth",max_depth)
        sb.YIELD("path")
        sb.RETURN("path")
        print(sb.BUILD())
        return sb.BUILD()
        

    def adamic_adar(self,name,node1,node2):
        sb = StringBuilder()
        sb.MATCH("n1",node1)
        sb.MATCH("n2",node2)
        sb.RETURN(f"gds.alpha.linkprediction.adamicAdar('{name}',n1, n2) AS score")
        return sb.BUILD()

    def subgraph(self,o_name,n_name,nodes,edges):
        if len(nodes) == 0:
            node = "*"
        else:
            node =  "n:" + " OR n:".join([f'`{n}`' for n in nodes])
        if len(edges) == 0:
            edge = "*"
        else:
            edge = "r:" + " OR r:".join([f'`{e}`' for e in edges])
        return f'''
        CALL gds.beta.graph.project.subgraph(
        '{n_name}',
        '{o_name}',
        '{node}',
        '{edge}'
        )
        YIELD graphName, fromGraphName, nodeCount, relationshipCount
        '''
    
