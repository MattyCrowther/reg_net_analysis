import os
from mdutils.mdutils import MdUtils
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import numpy as np
import networkx as nx
from collections import Counter
from collections import defaultdict

from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.model.model import model


out_dir = "network_report"
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
fn = os.path.join(out_dir,f'network_analysis_report.md')
md_file = MdUtils(file_name=fn, title='Network Analysis Report')



'''
NOTE @@@@@@@@
2. Write tests for what you have.
3. Start semantic analysis
'''

def analyse(graph):
    '''
    Analysis system just for neo4j graph
    '''
    assert(type(graph) == Neo4jStorage)
    md_file.new_paragraph("**Author:** Mcrowther  \n**Date:** 2025-05-21  \n**Project:** My Network")
    analyse_graph_metrics(graph)
    #analyse_semantics(graph)
    md_file.create_md_file()


def analyse_graph_metrics(graph):
    md_file.new_header(level=1, title='1. Graph Metrics')
    '''
    _report_basic_structure(graph)
    _report_degree_distribution(graph)
    _report_connected_components(graph)
    _report_shortest_path_metrics(graph)
    _report_density(graph)
    _report_clustering_coefficient(graph)
    _report_assortativity(graph)
    _report_centrality(graph)
    '''
    _report_node_similarity(graph)
    
def analyse_semantics(graph):
    md_file.new_header(level=1, title='2. Semantic Overview')
    md_file.new_paragraph(
        "This section provides a high-level semantic summary of the graph, including node and relationship type distributions, "
        "their connectivity, and data coverage."
    )

    # -------------------------------------
    # 2.1 Node Label Distribution
    # -------------------------------------
    md_file.new_header(level=2, title='2.1. Node Label Distribution')
    md_file.new_paragraph(
        "Nodes in the graph may belong to different conceptual categories (labels). "
        "This section summarizes the distribution of node labels to help characterize the semantic composition of the graph, "
        "including their frequency, connectivity, and property completeness."
    )

    label_counts = defaultdict(int)
    label_relationships = defaultdict(set)
    label_totals = defaultdict(int)
    label_property_counts = defaultdict(lambda: defaultdict(int))

    nodes = list(graph.get())  # cache all nodes
    for node in nodes:
        label = _get_name(node.object_type)
        label_counts[label] += 1
        label_totals[label] += 1

        for rel_type in node.relationships.keys():
            label_relationships[label].add(_get_name(rel_type))

        for prop in node.properties:
            if node.properties[prop] is not None:
                label_property_counts[label][prop] += 1

    headers = ["Label", "Node Count", "Connected Relationship Types", "Properties (Coverage %)"]
    table_data = []

    for label in sorted(label_counts, key=label_counts.get, reverse=True):
        count = label_counts[label]
        rels = ", ".join(sorted(label_relationships[label])) if label_relationships[label] else "—"
        props = label_property_counts[label]
        total = label_totals[label]
        coverage_list = [
            f"{_get_name(prop)} ({(count / total) * 100:.0f}%)"
            for prop, count in sorted(props.items(), key=lambda x: x[1], reverse=True)
        ]
        coverage_str = ", ".join(coverage_list) if coverage_list else "—"
        table_data.extend([label, str(count), rels, coverage_str])

    row_count = len(label_counts) + 1
    md_file.new_table(columns=4, rows=row_count, text=[*headers, *table_data], text_align='center')

    # -------------------------------------
    # 2.2 Relationship Type Semantics
    # -------------------------------------
    md_file.new_header(level=2, title='2.2. Relationship Type Semantics')
    md_file.new_paragraph(
        "This section summarizes each relationship type by how often it appears, the types of nodes it connects, "
        "and the most common label pairings. This helps uncover how entities interact in the graph."
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
                if target_node is None:
                    continue
                target_label = _get_name(target_node.object_type)

                rel_counts[rel_type] += 1
                rel_sources[rel_type].add(source_label)
                rel_targets[rel_type].add(target_label)
                rel_label_pairs[rel_type][(source_label, target_label)] += 1

    headers = ["Relationship Type", "Count", "Source Labels", "Target Labels", "Top Label Pairs"]
    table_data = []

    for rel_type in sorted(rel_counts, key=rel_counts.get, reverse=True):
        count = rel_counts[rel_type]
        sources = ", ".join(sorted(rel_sources[rel_type])) or "—"
        targets = ", ".join(sorted(rel_targets[rel_type])) or "—"

        top_pairs = sorted(
            rel_label_pairs[rel_type].items(), key=lambda x: x[1], reverse=True
        )[:3]
        pair_str = ", ".join(f"{s}→{t} ({c})" for ((s, t), c) in top_pairs) or "—"

        table_data.extend([rel_type, str(count), sources, targets, pair_str])

    row_count = len(rel_counts) + 1
    md_file.new_table(columns=5, rows=row_count,
                      text=[*headers, *table_data],
                      text_align='center')


def _report_basic_structure(graph):
    md_file.new_header(level=2, title='1.1. Basic Graph Structure')
    md_file.new_paragraph(
        "This section provides an overview of the graph's size and basic structure, "
        "including the number of nodes and edges, as well as the number of isolated nodes "
        "(nodes with no relationships). These metrics give a quick sense of the graph's scale and connectivity."
    )

    nc = graph.node_count()
    ec = graph.edge_count()
    isolated_nodes = graph.get_isolated_nodes()

    md_file.new_paragraph("**Graph Summary:**")
    md_file.new_line(f"- **Node Count:** {nc}")
    md_file.new_line(f"- **Edge Count:** {ec}")
    md_file.new_line(f"- **Isolated Nodes:** {len(isolated_nodes)}")

    md_file.new_paragraph("**Isolated Nodes:**")
    headers = ["#", "Label", "ID", "Properties"]
    table_data = []

    for idx, node in enumerate(isolated_nodes):
        label_str = _get_name(node.object_type)
        id_str = _get_name(node.identifier)
        props_str = "; ".join(
            f"{_get_name(k)}: {str(v)[:50]}{'…' if len(str(v)) > 50 else ''}" for k, v in node.properties.items()
        )
        table_data.extend([str(idx + 1), label_str, id_str, props_str])

    row_count = len(isolated_nodes) + 1
    md_file.new_table(columns=4, rows=row_count, text=[*headers, *table_data], text_align='center')


def _report_degree_distribution(graph):
    md_file.new_header(level=2, title='1.2. Degree Distribution')
    md_file.new_paragraph("The degree distribution shows how many connections each node has. "
                          "It reveals the network's connectivity pattern — whether most nodes are evenly connected, "
                          "or if there are hubs with disproportionately high degrees. A log-log scale is used to highlight "
                          "scale-free or power-law characteristics commonly seen in real-world networks.")

    degree_data = graph.get_degree_distribution()
    degrees, counts = zip(*degree_data)
    degree_array = np.repeat(degrees, counts)

    stats = {
        "Minimum degree": degree_array.min(),
        "Maximum degree": degree_array.max(),
        "Mean degree": degree_array.mean(),
        "Median degree": np.median(degree_array),
        "Standard deviation": degree_array.std()
    }

    md_file.new_paragraph("Summary of degree distribution statistics:")
    for k, v in stats.items():
        md_file.new_line(f"- **{k}:** {v:.2f}" if isinstance(v, float) else f"- **{k}:** {v}")

    plt.figure(figsize=(8, 5))
    plt.loglog(degrees, counts, marker='o', linestyle='None')
    plt.xlabel("Degree (log)")
    plt.ylabel("Node Count (log)")
    plt.title("Degree Distribution (Log-Log Scale)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"degree_distribution.png"))
    plt.close()
    md_file.new_line("![Degree Distribution](degree_distribution.png)")


def _report_connected_components(graph):
    md_file.new_header(level=2, title='1.3. Connected Components')
    md_file.new_paragraph("A connected component is a group of nodes where each node is reachable from any other node in the group. "
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

    md_file.new_line(f"- **Total components:** {total_components}")
    md_file.new_line(f"- **Total nodes:** {total_nodes}")
    md_file.new_line(f"- **Largest component size:** {largest}")
    md_file.new_line(f"- **Smallest component size:** {smallest}")
    md_file.new_line(f"- **Average component size:** {mean_size:.2f}")
    md_file.new_line(f"- **Singleton components (size 1):** {singleton_count}")
    md_file.new_line(f"- **% of nodes in largest component:** {percent_in_largest:.2%}")

    plt.figure(figsize=(10, 6))
    plt.hist(component_sizes, bins=30, edgecolor='black')
    plt.xlabel("Component Size")
    plt.ylabel("Number of Components")
    plt.title("Distribution of Connected Component Sizes")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"component_size_distribution.png"))
    plt.close()
    md_file.new_line("![Component Distribution](component_size_distribution.png)")


def _report_shortest_path_metrics(graph):
    md_file.new_header(level=2, title='1.4. Shortest Path Metrics')
    md_file.new_paragraph("This section summarizes global path-based properties of the network. It analyzes shortest paths "
                          "between all pairs of nodes to calculate metrics such as diameter (the longest shortest path), "
                          "average path length, and effective diameter (90th percentile). These measures reflect how efficiently "
                          "information can spread across the network.")

    res = graph.project.full_graph()
    sps = graph.procedure.all_shortest_path(res.name())
    filtered = np.array([dist for _, dist, _ in sps if dist > 0])

    diameter = filtered.max()
    avg_path_length = filtered.mean()
    effective_diameter = np.percentile(filtered, 90)
    harmonic_mean = np.mean(1 / filtered)
    median_path = np.median(filtered)
    min_path = filtered.min()

    md_file.new_line(f"- **Minimum shortest path:** {min_path}")
    md_file.new_line(f"- **Maximum shortest path (Diameter):** {diameter}")
    md_file.new_line(f"- **Median shortest path:** {median_path}")
    md_file.new_line(f"- **Average shortest path length:** {avg_path_length:.4f}")
    md_file.new_line(f"- **Effective diameter (90th percentile):** {effective_diameter:.2f}")
    md_file.new_line(f"- **Harmonic mean distance (Global efficiency):** {harmonic_mean:.4f}")

    counter = Counter(filtered)
    path_lengths, frequencies = zip(*sorted(counter.items()))

    plt.figure(figsize=(8, 5))
    plt.bar(path_lengths, frequencies, edgecolor='black')
    plt.xlabel("Shortest Path Length")
    plt.ylabel("Frequency")
    plt.title("Distribution of Shortest Path Lengths")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"shortest_path_distribution.png"))
    plt.close()
    md_file.new_line("![Shortest Path Distribution](shortest_path_distribution.png)")


def _report_density(graph):
    md_file.new_header(level=2, title='1.5. Graph Density & Reciprocity')
    
    md_file.new_paragraph(
        "This section describes the network's edge structure in terms of density and reciprocity. "
        "**Density** measures how many of the possible connections between nodes are actually present. "
        "**Reciprocity** applies to directed graphs and indicates how often relationships are bidirectional."
    )
    res = graph.project.full_graph()
    
    md_file.new_paragraph("**Density** is the proportion of possible edges that actually exist in the graph.")
    
    density = graph.procedure.density(res.name())
    md_file.new_line(f"- **Calculated Density:** {density:.6f}%")

    md_file.new_paragraph("**Reciprocity** measures the proportion of edges that are reciprocated in a directed graph.")
    reciprocity = graph.get_reciprocity()
    md_file.new_line(f"- **Calculated Reciprocity:** {reciprocity:.6f}")


def _report_clustering_coefficient(graph):
    md_file.new_header(level=2, title='1.6. Clustering Coefficient')
    md_file.new_paragraph(
        "Clustering coefficient measures the degree to which nodes in a graph tend to cluster together. "
        "It reflects how tightly knit the neighborhood of each node is. This section includes both the "
        "**global clustering coefficient**, which summarizes the overall tendency of the network to form triangles, "
        "and the **average local clustering coefficient**, which reflects the mean tendency of individual nodes "
        "to form clusters. High clustering often indicates redundant paths and community structure."
    )
    md_file.new_paragraph(
        "The global coefficient is computed as the ratio of the number of closed triplets "
        "(triangles) to the total number of triplets (both open and closed). "
        "The local coefficient for a node is based on the number of links between its neighbors."
    )
    # Note to self. Needs to be tested. When created, the graph had 0 triangles.
    res = graph.project.full_graph(directed=False)
    triangles = graph.procedure.triangles(res.name())
    average_lcc = graph.procedure.average_local_clustering_coefficient(res.name())
    global_clustering = graph.procedure.global_clustering_coefficient(res.name())
    md_file.new_line(f"- **Global Clustering Coefficient:** {global_clustering:.4f}")
    md_file.new_line(f"- **Average Local Clustering Coefficient:** {average_lcc:.4f}")

    triangle_counts = [count for _, count in triangles]

    distribution = Counter(triangle_counts)
    sorted_dist = dict(sorted(distribution.items()))

    plt.figure(figsize=(8, 5))
    plt.bar(sorted_dist.keys(), sorted_dist.values(), edgecolor='black')
    plt.xlabel("Number of Triangles")
    plt.ylabel("Number of Nodes")
    plt.title("Distribution of Triangle Counts per Node")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"triangle_distribution.png"))
    plt.close()

    md_file.new_line("![Triangle Distribution](triangle_distribution.png)")


def _report_assortativity(graph):
    md_file.new_header(level=2, title='1.7. Assortativity')

    md_file.new_paragraph(
        "Assortativity measures the similarity of connections in the network with respect to the node degree. "
        "**Degree assortativity** specifically quantifies whether nodes with similar numbers of connections tend to be linked. "
        "A positive assortativity coefficient indicates that nodes tend to connect with others of similar degree (assortative mixing), "
        "while a negative coefficient suggests connections between nodes of differing degree (disassortative mixing). "
    )

    res = graph.project.full_graph()
    assortativity = graph.procedure.degree_assortativity(res.name())
    md_file.new_line(f"- **Degree Assortativity Coefficient:** {assortativity:.4f}")


def _report_centrality(graph):
    md_file.new_header(level=2, title='1.8. Centrality Metrics')
    res = graph.project.full_graph()

    md_file.new_paragraph(
        "Centrality metrics quantify the relative importance or influence of individual nodes within the network. "
        "These measures are vital for understanding how information, influence, or control flows through the graph. "
        "Different centrality metrics capture different notions of influence — from local connectivity to global reach."
    )

    _report_single_centrality(
        title="Degree Centrality",
        description="Measures the number of direct connections a node has. High degree centrality indicates a node is locally well-connected and potentially influential within its immediate neighborhood.",
        procedure_fn=lambda: graph.procedure.degree_centrality(res.name()),
        score_format="{:.2f}",
        filename_prefix="degree_centrality"
    )

    _report_single_centrality(
        title="Betweenness Centrality",
        description="Captures how often a node lies on the shortest paths between other nodes. Nodes with high betweenness act as bridges or brokers, controlling the flow of information between different parts of the network.",
        procedure_fn=lambda: graph.procedure.betweenness_centrality(res.name()),
        filename_prefix="betweenness_centrality"
    )

    _report_single_centrality(
        title="Closeness Centrality",
        description="Reflects how close a node is to all other nodes in the network. Nodes with high closeness can quickly interact with all others and are typically efficient spreaders of information.",
        procedure_fn=lambda: graph.procedure.closeness_centrality(res.name()),
        filename_prefix="closeness_centrality"
    )

    _report_single_centrality(
        title="PageRank",
        description="A probability-based measure originally developed by Google to rank web pages. It evaluates the influence of a node based not just on its connections, but also on the importance of those it's connected to.",
        procedure_fn=lambda: graph.procedure.page_rank(res.name()),
        score_format="{:.6f}",
        filename_prefix="pagerank"
    )

    _report_single_centrality(
        title="Eigenvector Centrality",
        description="Evaluates a node’s influence based on the principle that connections to high-scoring nodes contribute more to the score of the node. "
                    "Unlike degree centrality, which counts all neighbors equally, eigenvector centrality gives more weight to connections with influential nodes.",
        procedure_fn=lambda: graph.procedure.eigenvector_centrality(res.name()),
        score_format="{:.6f}",
        filename_prefix="eigenvector_centrality"
    )


def _report_node_similarity(graph):
    md_file.new_header(level=2, title='1.9. Node Similarity Metrics')
    res = graph.project.full_graph()

    md_file.new_paragraph(
        "This section explores similarity relationships between nodes based on structural or attribute-based features. "
        "Node similarity metrics are useful for tasks such as recommendation, clustering, link prediction, and entity resolution. "
        "We focus on structural similarity, which compares the neighborhoods of nodes to identify similar roles or positions in the graph."
    )

    # Cosine Similarity (or Jaccard, etc.)
    md_file.new_header(level=3, title='**Cosine Similarity (Top-K):**')
    md_file.new_line(
        "Cosine similarity compares nodes based on the overlap of their neighbors. "
        "Each node is treated as a vector of connections, and the cosine of the angle between these vectors indicates similarity. "
        "This method is commonly used in recommendation systems and for detecting structural equivalence."
    )

    similarity_data = graph.procedure.node_similarity(res.name())

    # Summary statistics
    similarities = [sim for _, _, sim in similarity_data]
    similarities_np = np.array(similarities)

    stats = {
        "Pair Count": len(similarities),
        "Maximum Similarity": similarities_np.max(),
        "Minimum Similarity": similarities_np.min(),
        "Mean Similarity": similarities_np.mean(),
        "Median Similarity": np.median(similarities_np),
        "Standard deviation": similarities_np.std()
    }

    md_file.new_paragraph("**Summary statistics for top-K node similarity:**")
    for k, v in stats.items():
        md_file.new_line(f"- **{k}:** {v:.4f}" if isinstance(v, float) else f"- **{k}:** {v}")

    # Histogram
    plt.figure(figsize=(8, 5))
    plt.hist(similarities, bins=30, edgecolor='black')
    plt.xlabel("Cosine Similarity Score")
    plt.ylabel("Number of Node Pairs")
    plt.title("Distribution of Node Similarity Scores")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "node_similarity_distribution.png"))
    plt.close()
    md_file.new_line("![Node Similarity Distribution](node_similarity_distribution.png)")

    # Visual context
    md_file.new_paragraph("**Top 10 most similar node pairs:**")
    md_file.new_line(
        "The following visualizations show the top 10 most structurally similar node pairs in the graph, "
        "based on cosine similarity. Each subgraph includes the nodes and their immediate neighborhoods (depth=1). "
        "These visual summaries help identify similar roles or positions among the most comparable entities."
    )

    # Visualize top-k similar pairs
    top_pairs = sorted(similarity_data, key=lambda x: x[2], reverse=True)[:10]
    res = graph.project.full_graph(directed=False)

    for idx, (node_a, node_b, score) in enumerate(top_pairs):
        nx_graph = nx.DiGraph()
        

        nx_graph.add_node(node_a.identifier,
                          label=node_a.object_type,
                          **node_a.properties)
        for e,v in graph.get_edges(identifier=node_a.identifier):
            nx_graph.add_node(v.identifier,
                            label=v.object_type,
                            **v.properties)
            nx_graph.add_edge(node_a.identifier,v.identifier, type=e)

        nx_graph.add_node(node_b.identifier,
                          label=node_b.object_type,
                          **node_b.properties)
        for e,v in graph.get_edges(identifier=node_b.identifier):
            nx_graph.add_node(v.identifier,
                            label=v.object_type,
                            **v.properties)
            nx_graph.add_edge(node_b.identifier,v.identifier, type=e)
        

        label_a = _get_name(node_a.object_type)
        id_a = _get_name(node_a.identifier)
        label_b = _get_name(node_b.object_type)
        id_b = _get_name(node_b.identifier)

        md_file.new_line(
            f"**Pair {idx + 1}:** Comparing `{label_a}` (`{id_a}`) and `{label_b}` (`{id_b}`) "
            f"with a similarity score of **{score:.4f}**."
        )

        out_path = os.path.join(out_dir, f"similarity_pair_{idx+1}.png")
        _visualise_network(
            nx_graph,
            filename=out_path,
            title=f"Node Similarity Pair {idx+1} (Score: {score:.2f})"
        )

        md_file.new_line(f"![Node Similarity Pair {idx+1}](similarity_pair_{idx+1}.png)")




def _report_single_centrality(title, description, 
                              procedure_fn, 
                              score_format="{:.4f}", 
                              filename_prefix="centrality"):
    md_file.new_header(level=3, title=f'**{title}:**')
    md_file.new_line(description)

    centrality_data = procedure_fn()

    scores = [score for _, score in centrality_data]
    scores_np = np.array(scores)

    stats = {
        "Minimum": scores_np.min(),
        "Maximum": scores_np.max(),
        "Mean": scores_np.mean(),
        "Median": np.median(scores_np),
        "Standard deviation": scores_np.std()
    }

    md_file.new_paragraph(f"**Summary statistics for {title.lower()}:**")
    for k, v in stats.items():
        md_file.new_line(f"- **{k}:** {score_format.format(v)}")

    plt.figure(figsize=(8, 5))
    plt.hist(scores, bins=30, edgecolor='black')
    plt.yscale('log')
    plt.xlabel(f"{title} Score")
    plt.ylabel("Number of Nodes (log)")
    plt.title(f"{title} Distribution")
    plt.tight_layout()
    filename = f"{filename_prefix.lower()}_distribution.png"
    plt.savefig(os.path.join(out_dir, filename))
    plt.close()
    md_file.new_line(f"![{title} Distribution]({filename})")

    md_file.new_paragraph(f"**Top 10 nodes by {title.lower()}:**")
    headers = ["Rank", "Label", "ID", f"{title} Score"]
    table_data = []

    top_nodes = sorted(centrality_data, key=lambda x: x[1], reverse=True)[:10]
    for idx, (node, score) in enumerate(top_nodes):
        label_str = _get_name(node.object_type)
        id_str = _get_name(node.identifier)
        table_data.extend([str(idx + 1), label_str, id_str, score_format.format(score)])

    md_file.new_table(columns=4, rows=11, text=[*headers, *table_data], text_align='center')




def _visualise_network(G, filename, title="", node_labels=True):
    """
    Renders and saves a network visualization using matplotlib and networkx.

    Args:
        G (networkx.Graph or networkx.DiGraph): The graph to visualize.
        filename (str): Output path for the PNG file.
        title (str): Optional plot title.
        node_labels (bool): Whether to show node identifiers in the graph.
    """
    plt.figure(figsize=(6, 6))
    pos = nx.spring_layout(G, seed=42)

    # Shortened node ID labels for display
    labels = {
        n: (_get_name(n)[:12] + '…' if len(_get_name(n)) > 12 else _get_name(n))
        for n in G.nodes
    }

    # Node label attribute (e.g., 'Gene', 'Transcript')
    node_labels_attr = nx.get_node_attributes(G, 'label')

    # Extract and clean primary labels
    primary_labels = {
        n: _get_name(label) if label else "Unknown"
        for n, label in node_labels_attr.items()
    }

    unique_labels = sorted(set(primary_labels.values()))

    # Color mapping for labels
    color_map = plt.colormaps.get_cmap('tab10')
    label_to_color = {
        label: mcolors.rgb2hex(color_map(i % 10))
        for i, label in enumerate(unique_labels)
    }

    node_colors = [
        label_to_color.get(primary_labels.get(n, "Unknown"), "#cccccc")
        for n in G.nodes
    ]

    nx.draw(
        G, pos,
        with_labels=node_labels,
        labels=labels,
        node_color=node_colors,
        edge_color='gray',
        node_size=600,
        font_size=6
    )

    # Add legend
    legend_handles = [
        Patch(color=color, label=label)
        for label, color in label_to_color.items()
    ]

    plt.legend(
        handles=legend_handles,
        title="Node Labels",
        loc='best',
        fontsize='small',
        title_fontsize='small',
        frameon=True
    )

    plt.title(title)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()



def _get_name(uri):
    return uri.split("/")[-1]