import numpy as np
from collections import Counter
from collections import defaultdict

from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model


nv_title = str(model.identifiers.external.title)

def analyse(graph):
    '''
    Analysis system just for neo4j graph
    '''
    data = {}
    assert(type(graph) == Neo4jStorage)
    data["graph"] = analyse_graph_metrics(graph)
    data["semantic"] = analyse_semantics(graph)
    return data


def analyse_graph_metrics(graph):
    description = (
        "This section provides structural and topological insights into the graph. "
        "It includes statistics like node/edge counts, path metrics, clustering behavior, centrality measures, "
        "and node similarity — all of which help characterize how the network is organized and how it behaves."
    )

    return {
        "description": description,
        "basic_structure": _report_basic_structure(graph),
        "degree_distribution": _report_degree_distribution(graph),
        "connected_components": _report_connected_components(graph),
        "shortest_paths": _report_shortest_path_metrics(graph),
        "density": _report_density(graph),
        "clustering_coefficient": _report_clustering_coefficient(graph),
        "centrality_metrics": _report_centrality(graph),
        "assortativity": _report_assortativity(graph),
        "node_similarity": _report_node_similarity(graph),
    }


def analyse_semantics(graph):
    description = (
        "This section provides a high-level semantic summary of the "
        "graph, including node and relationship type distributions, "
        "their connectivity, and data coverage."
    )

    nodes = list(graph.get())
    return {
        "description": description,
        "node_label_distribution": _node_label_distribution(nodes),
        "relationship_type_semantics": _relationship_type_semantics(nodes),
        "sequence_similarity": _sequence_similarity(nodes)
    }


def _report_basic_structure(graph):
    description = ("This section provides an overview of the graph's size and basic structure, " + 
                   "including the number of nodes and edges, as well as the number of isolated nodes " + 
                   "(nodes with no relationships). These metrics give a quick sense of the graph's scale and connectivity.")
    data = {"description" : description,
            "metrics" : {}}

    data["metrics"]["node_count"] = graph.node_count()
    data["metrics"]["edge_count"] = graph.edge_count()
    data["metrics"]["isolated_nodes"] = [_generate_entity_dict(n) for 
                                         n in graph.get_isolated_nodes()]
    return data


def _report_degree_distribution(graph):
    description = ("The degree distribution shows how many connections each node has. "
                    "It reveals the network's connectivity pattern — whether most nodes are evenly connected, "
                    "or if there are hubs with disproportionately high degrees. A log-log scale is used to highlight "
                    "scale-free or power-law characteristics commonly seen in real-world networks.")
    degree_data = graph.get_degree_distribution()
    degrees, counts = zip(*degree_data)
    degree_array = np.repeat(degrees, counts)
    data = {"description" : description,
            "metrics" : {"minimum_degree": int(degree_array.min()),
                         "maximum_degree": int(degree_array.max()),
                         "mean_degree": float(degree_array.mean()),
                         "median_degree": np.median(degree_array),
                         "standard_deviation": degree_array.std(),
                         }}#"degree_counts" : [degrees, counts]}}
    return data


def _report_connected_components(graph):
    description = ("A connected component is a group of nodes where each node is reachable from any other node in the group. "
                "This section summarizes the number and size of connected components, which indicates how fragmented or cohesive "
                "the graph is. A well-integrated graph usually has a single large component containing most of the nodes.")
    
    res = graph.project.full_graph()
    components = graph.procedure.get_components(res.name())
    component_sizes = [len(c) for c in components.values()]

    total_components = len(component_sizes)
    largest = max(component_sizes)
    smallest = min(component_sizes)
    mean_size = sum(component_sizes) / total_components
    singleton_count = sum(1 for s in component_sizes if s == 1)
    total_nodes = sum(component_sizes)
    percent_in_largest = largest / total_nodes

    data = {"description" : description,
            "metrics" : {"total_components": total_components,
                         "total_nodes": total_nodes,
                         "largest_component_size": largest,
                         "smallest_component_size": smallest,
                         "average_component_size": round(mean_size, 2),
                         "singleton_components": singleton_count,
                         "percent_node_in_largest_component": f"{percent_in_largest:.2%}",
                         }}#"connected_component_sizes" : [len(c) for c in components.values()]}}
    return data


def _report_shortest_path_metrics(graph):
    description = (
        "This section summarizes global path-based properties of the network. It analyzes shortest paths "
        "between all pairs of nodes to calculate metrics such as diameter (the longest shortest path), "
        "average path length, and effective diameter (90th percentile). These measures reflect how efficiently "
        "information can spread across the network."
    )

    res = graph.project.full_graph()
    sps = graph.procedure.all_shortest_path(res.name())
    filtered = np.array([dist for _, dist, _ in sps if dist > 0])

    diameter = filtered.max()
    avg_path_length = filtered.mean()
    effective_diameter = np.percentile(filtered, 90)
    harmonic_mean = np.mean(1 / filtered)
    median_path = np.median(filtered)
    min_path = filtered.min()

    data = {
        "description": description,
        "metrics": {
            "minimum_shortest_path": int(min_path),
            "maximum_shortest_path": int(diameter),
            "median_shortest_path": float(median_path),
            "average_shortest_path_length": round(avg_path_length, 4),
            "effective_diameter": round(effective_diameter, 2),
            "harmonic_mean_distance": round(harmonic_mean, 4)
        },
    }

    return data


def _report_density(graph):
    description = (
        "This section describes the network's edge structure in terms of density and reciprocity. "
        "**Density** measures how many of the possible connections between nodes are actually present. "
        "**Reciprocity** applies to directed graphs and indicates how often relationships are bidirectional."
    )

    res = graph.project.full_graph()
    density = graph.procedure.density(res.name())
    reciprocity = graph.get_reciprocity()

    data = {
        "description": description,
        "metrics": {
            "calculated_density": round(density, 6),
            "calculated_reciprocity": round(reciprocity, 6)
        },
    }

    return data


def _report_clustering_coefficient(graph):
    description = (
        "Clustering coefficient measures the degree to which nodes in a graph tend to cluster together. "
        "It reflects how tightly knit the neighborhood of each node is. This section includes both the "
        "**global clustering coefficient**, which summarizes the overall tendency of the network to form triangles, "
        "and the **average local clustering coefficient**, which reflects the mean tendency of individual nodes "
        "to form clusters. High clustering often indicates redundant paths and community structure.\n\n"
        "The global coefficient is computed as the ratio of the number of closed triplets "
        "(triangles) to the total number of triplets (both open and closed). "
        "The local coefficient for a node is based on the number of links between its neighbors."
    )

    res = graph.project.full_graph(directed=False)
    triangles = graph.procedure.triangles(res.name())
    average_lcc = graph.procedure.average_local_clustering_coefficient(res.name())
    global_clustering = graph.procedure.global_clustering_coefficient(res.name())

    triangle_counts = [count for _, count in triangles]
    triangle_count_distribution = dict(sorted(Counter(triangle_counts).items()))
    max_triangles = max(triangle_counts) if triangle_counts else 0
    mean_triangles = np.mean(triangle_counts) if triangle_counts else 0
    median_triangles = np.median(triangle_counts) if triangle_counts else 0

    metrics = {
        "global_clustering_coefficient": round(global_clustering, 4),
        "average_local_clustering_coefficient": round(average_lcc, 4),
        "max_triangles_per_node": int(max_triangles),
        "mean_triangles_per_node": round(mean_triangles, 2),
        "median_triangles_per_node": int(median_triangles),
        "triangle_count_distribution": triangle_count_distribution
    }

    return {
        "description": description,
        "metrics": metrics
    }


def _report_assortativity(graph):
    description = (
        "Assortativity measures the similarity of connections in the network with respect to the node degree. "
        "**Degree assortativity** specifically quantifies whether nodes with similar numbers of connections tend to be linked. "
        "A positive assortativity coefficient indicates that nodes tend to connect with others of similar degree (assortative mixing), "
        "while a negative coefficient suggests connections between nodes of differing degree (disassortative mixing)."
    )

    res = graph.project.full_graph()
    assortativity = graph.procedure.degree_assortativity(res.name())

    return {
        "description": description,
        "metrics": {
            "degree_assortativity_coefficient": round(assortativity, 4)
        }
    }


def _report_centrality(graph):
    description = (
        "Centrality metrics quantify the relative importance or influence of individual nodes within the network. "
        "These measures are vital for understanding how information, influence, or control flows through the graph. "
        "Different centrality metrics capture different notions of influence — from local connectivity to global reach."
    )

    res = graph.project.full_graph()

    centrality_defs = {
        "degree_centrality": {
            "description": "Measures the number of direct connections a node has. High degree centrality indicates a node is locally well-connected and potentially influential within its immediate neighborhood.",
            "fn": lambda: graph.procedure.degree_centrality(res.name()),
            "format": "{:.2f}"
        },
        "betweenness_centrality": {
            "description": "Captures how often a node lies on the shortest paths between other nodes. Nodes with high betweenness act as bridges or brokers, controlling the flow of information between different parts of the network.",
            "fn": lambda: graph.procedure.betweenness_centrality(res.name()),
            "format": "{:.4f}"
        },
        "closeness_centrality": {
            "description": "Reflects how close a node is to all other nodes in the network. Nodes with high closeness can quickly interact with all others and are typically efficient spreaders of information.",
            "fn": lambda: graph.procedure.closeness_centrality(res.name()),
            "format": "{:.4f}"
        },
        "page_rank": {
            "description": "A probability-based measure originally developed by Google to rank web pages. It evaluates the influence of a node based not just on its connections, but also on the importance of those it's connected to.",
            "fn": lambda: graph.procedure.page_rank(res.name()),
            "format": "{:.6f}"
        },
        "eigenvector_centrality": {
            "description": "Evaluates a node’s influence based on the principle that connections to high-scoring nodes contribute more to the score of the node. "
                           "Unlike degree centrality, which counts all neighbors equally, eigenvector centrality gives more weight to connections with influential nodes.",
            "fn": lambda: graph.procedure.eigenvector_centrality(res.name()),
            "format": "{:.6f}"
        }
    }

    metrics = {
        name: {
            "description": config["description"],
            **_compute_single_centrality(
                procedure_fn=config["fn"],
                score_format=config["format"]
            )
        }
        for name, config in centrality_defs.items()
    }

    return {
        "description": description,
        "metrics": metrics
    }


def _report_node_similarity(graph):
    description = (
        "This section explores similarity relationships between nodes based on structural or attribute-based features. "
        "Node similarity metrics are useful for tasks such as recommendation, clustering, link prediction, and entity resolution. "
        "We focus on structural similarity, which compares the neighborhoods of nodes to identify similar roles or positions in the graph.\n\n"
        "Cosine similarity compares nodes based on the overlap of their neighbors. "
        "Each node is treated as a vector of connections, and the cosine of the angle between these vectors indicates similarity. "
        "This method is commonly used in recommendation systems and for detecting structural equivalence."
    )

    res = graph.project.full_graph()
    similarity_data = graph.procedure.node_similarity(res.name())

    similarities = [sim for _, _, sim in similarity_data]
    similarities_np = np.array(similarities)

    stats = {
        "pair_count": len(similarities),
        "maximum_similarity": round(similarities_np.max(), 4),
        "minimum_similarity": round(similarities_np.min(), 4),
        "mean_similarity": round(similarities_np.mean(), 4),
        "median_similarity": round(np.median(similarities_np), 4),
        "standard_deviation": round(similarities_np.std(), 4),
        #"similar_nodes" : similarities
    }

    # Top 10 most similar pairs
    top_pairs = sorted(similarity_data, key=lambda x: x[2], reverse=True)[:10]

    top_similar = [
        {
            "rank": i + 1,
            "node_a_label": _get_name(node_a.object_type),
            "node_a_id": _generate_entity_dict(node_a),
            "node_b_label": _get_name(node_b.object_type),
            "node_b_id": _generate_entity_dict(node_b),
            "similarity_score": f"{score:.4f}"
        }
        for i, (node_a, node_b, score) in enumerate(top_pairs)
    ]

    return {
        "description": description,
        "metrics": {
            **stats,
            "similar_node_pairs": top_similar
        }
    }

def _generate_entity_dict(node):
    return {"title" : node.properties.get(nv_title,["No Title"])[0],
            "id" : node.identifier}

def _compute_single_centrality(procedure_fn, score_format="{:.4f}"):
    """
    Compute a single centrality and return stats + top 10 nodes.
    """
    centrality_data = procedure_fn()
    scores = [score for _, score in centrality_data]
    scores_np = np.array(scores)

    top_nodes = sorted(centrality_data, key=lambda x: x[1], reverse=True)[:10]
    top_10 = [
        {
            "rank": idx + 1,
            "label": _get_name(node.object_type),
            "id": _generate_entity_dict(node),
            "score": score_format.format(score)
        }
        for idx, (node, score) in enumerate(top_nodes)
    ]

    return {
        "minimum": float(np.min(scores_np)),
        "maximum": float(np.max(scores_np)),
        "mean": float(np.mean(scores_np)),
        "median": float(np.median(scores_np)),
        "standard_deviation": float(np.std(scores_np)),
        #"centrality_score" : scores,
        "top_nodes": top_10
    }


def _node_label_distribution(nodes):
    description = (
        "Nodes in the graph may belong to different conceptual categories (labels). "
        "This summarizes label frequency, the diversity of their relationship types, "
        "and property coverage per label to characterize semantic structure."
    )

    label_counts = defaultdict(int)
    label_relationships = defaultdict(set)
    label_totals = defaultdict(int)
    label_property_counts = defaultdict(lambda: defaultdict(int))

    for node in nodes:
        label = _get_name(node.object_type)
        label_counts[label] += 1
        label_totals[label] += 1

        for rel_type in node.relationships:
            label_relationships[label].add(_get_name(rel_type))

        for prop, val in node.properties.items():
            if val is not None:
                label_property_counts[label][prop] += 1

    metrics = {"groupings" : []}
    for label in sorted(label_counts, key=label_counts.get, reverse=True):
        total = label_totals[label]
        props = label_property_counts[label]
        coverage = {
            _get_name(p): f"{(c / total) * 100:.0f}%"
            for p, c in sorted(props.items(), key=lambda x: x[1], reverse=True)
        }

        metrics["groupings"].append({
            "label" : label,
            "node_count": label_counts[label],
            "connected_relationship_types": sorted(label_relationships[label]) or [],
            "property_coverage": coverage or {}
        })

    return {
        "description": description,
        "metrics": metrics
    }


def _relationship_type_semantics(nodes):
    description = (
        "This summarizes each relationship type by how often it appears, what node types it connects, "
        "and the most common label pairings."
    )

    rel_counts = defaultdict(int)
    rel_sources = defaultdict(set)
    rel_targets = defaultdict(set)
    rel_label_pairs = defaultdict(lambda: defaultdict(int))
    id_to_node = {str(n.identifier): n for n in nodes}

    for node in nodes:
        source_label = _get_name(node.object_type)

        for rel_type, target_ids in node.relationships.items():
            rel_type = _get_name(rel_type)

            for target_id in target_ids:
                target_node = id_to_node.get(str(target_id))
                if not target_node:
                    continue
                target_label = _get_name(target_node.object_type)
                rel_counts[rel_type] += 1
                rel_sources[rel_type].add(source_label)
                rel_targets[rel_type].add(target_label)
                rel_label_pairs[rel_type][(source_label, target_label)] += 1

    metrics = {"groupings" : []}
    for rel_type in sorted(rel_counts, key=rel_counts.get, reverse=True):
        top_pairs = sorted(rel_label_pairs[rel_type].items(), key=lambda x: x[1], reverse=True)[:3]
        pair_strs = [f"{s}→{t} ({c})" for (s, t), c in top_pairs]
        metrics["groupings"].append({
            "relationship_type" : rel_type,
            "count": rel_counts[rel_type],
            "source": sorted(rel_sources[rel_type]),
            "target": sorted(rel_targets[rel_type]),
            "label_pairs": pair_strs
        })

    return {
        "description": description,
        "metrics": metrics
    }


def _sequence_similarity(nodes):
    description = (
        "This section compares physical entity nodes by sequence. "
        "It identifies exact sequence matches across nodes and lists shared identifiers."
    )

    sequence_predicate = str(model.identifiers.predicates.has_sequence)
    sequence_dict = defaultdict(list)

    for node in nodes:
        seq = node.properties.get(sequence_predicate)
        if seq:
            sequence_dict[seq[0].lower()].append(node)

    shared_sequences = {
        seq: [_generate_entity_dict(i) for i in ids]
        for seq, ids in sequence_dict.items()
        if len(ids) > 1
    }

    return {
        "description": description,
        "metrics": {"shared_sequences": shared_sequences or {}}
    }


def _get_name(uri):
    return uri.split("/")[-1]