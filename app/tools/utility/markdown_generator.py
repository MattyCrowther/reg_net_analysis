import os
import datetime
from numpy import int64
from mdutils.mdutils import MdUtils
import matplotlib.pyplot as plt
from collections import Counter

IMAGES_DIR = "network_report"
filename= os.path.join(IMAGES_DIR,
                       "network_analysis_report.md")
def get_filename():
    return filename

def _make_plot(
    md_file,
    data,
    *,
    kind: str,
    filename: str,
    title: str,
    xlabel: str,
    ylabel: str,
    log_axes: tuple[str, ...] = (),
    bins: int | None = None,
    figsize: tuple[int, int] = (8, 5),
):
    """
    Generic distribution plot:
     - kind='hist'   → plt.hist()
     - kind='bar'    → plt.bar() (data must be dict-like)
     - kind='scatter'→ plt.loglog() (data must be (x, y))
    """
    fig, ax = plt.subplots(figsize=figsize)

    if kind == 'hist':
        ax.hist(data, bins=bins or 30, edgecolor='black')
    elif kind == 'bar':
        # Expect data to be a dict or Counter
        items = data.items() if hasattr(data, 'items') else Counter(data).items()
        xs, ys = zip(*sorted(items))
        ax.bar(xs, ys, edgecolor='black')
    elif kind == 'scatter':
        x, y = data
        ax.loglog(x, y, marker='o', linestyle='None')
    else:
        raise ValueError(f"Unknown kind: {kind}")

    for axis in log_axes:
        ax.set_yscale('log') if axis == 'y' else ax.set_xscale('log')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    fig.tight_layout()
    out = os.path.join(IMAGES_DIR, filename)
    fig.savefig(out)
    plt.close(fig)

    md_file.new_line(f"![{title}]({filename})")


# Then each specific function becomes a one-liner:
def _plot_degree_distribution(md_file, degree_counts, title=None):
    degrees, counts = degree_counts
    _make_plot(
        md_file, 
        (degrees, counts),
        kind='scatter',
        filename="degree_distribution.png",
        title="Degree Distribution (Log-Log Scale)",
        xlabel="Degree (log)",
        ylabel="Node Count (log)",
        log_axes=('x','y'),
        figsize=(8,5),
    )

def _plot_connected_components(md_file, component_sizes, title=None):
    _make_plot(
        md_file,
        component_sizes,
        kind='hist',
        filename="component_size_distribution.png",
        title="Connected Component Size Distribution",
        xlabel="Component Size",
        ylabel="Number of Components",
        bins=30,
        figsize=(10,6),
    )

def _plot_triangle_count_distribution(md_file, triangle_counts, title=None):
    dist = Counter(triangle_counts)
    _make_plot(
        md_file,
        dist,
        kind='bar',
        filename="triangle_distribution.png",
        title="Distribution of Triangle Counts per Node",
        xlabel="Number of Triangles",
        ylabel="Number of Nodes",
    )

def _plot_node_similarities(md_file, similarities, title=None):
    _make_plot(
        md_file,
        similarities,
        kind='hist',
        filename="node_similarity_distribution.png",
        title="Distribution of Node Similarity Scores",
        xlabel="Cosine Similarity Score",
        ylabel="Number of Node Pairs",
        bins=30,
    )

def _plot_centrality_score(md_file, scores, title):
    fname = f"{title.replace(' ','_').lower()}_distribution.png"
    _make_plot(
        md_file,
        scores,
        kind='hist',
        filename=fname,
        title=f"{_beautify(title)} Distribution",
        xlabel=f"{_beautify(title)} Score",
        ylabel="Number of Nodes",
        bins=30,
        log_axes=('y',),
    )

# Because its throwaway code, just statically define the parts which can be plotted.
plot_dict = {"degree_counts" : _plot_degree_distribution,
             "connected_component_sizes" : _plot_connected_components,
             "triangle_count_distribution" : _plot_triangle_count_distribution,
             "similar_nodes": _plot_node_similarities,
             "centrality_score" : _plot_centrality_score}

def generate_markdown(
    data,
    author="Mcrowther",
    project="Graph Metrics",
    date=None
):
    """
    Generate a Markdown report from nested analysis data using MdUtils for tables and lists.

    Returns the path to the generated markdown file.
    """
    if date is None:
        date = datetime.date.today().isoformat()

    os.makedirs(IMAGES_DIR, exist_ok=True)

    md_file = MdUtils(file_name=filename, title='')
    md_file.new_header(title='Network Analysis Report',level=1)
    md_file.new_paragraph('========================\n')

    md_file.new_paragraph(f"**Author:** {author}  ")
    md_file.new_paragraph(f"**Date:** {date}  ")
    md_file.new_paragraph(f"**Project:** {project}\n")

    md_file.new_header(title='Graph Metrics',level=2)
    desc = _get_description(data["graph"])
    md_file.new_paragraph(desc)
    _render_node(data["graph"], md_file)

    md_file.new_header(title='Semantic Metrics',level=2)
    desc = _get_description(data["semantic"])
    md_file.new_paragraph(desc)
    _render_node(data["semantic"], md_file)

    md_file.create_md_file()
    return filename


def _render_node(node, md_file: MdUtils):
    """
    Recursively generate sections, tables, and lists for any node.
    - level: heading depth (#)
    - prefix: numbering prefix
    """
    if not isinstance(node,dict):
        raise ValueError()

    for metric_group,metrics in node.items():
        if metric_group == "description":
            continue

        md_file.new_header(title=_beautify(metric_group),level=3)
        grp_desc = _get_description(metrics)
        md_file.new_paragraph(grp_desc)
        metrics = metrics.get("metrics")
        for metric_type,value in metrics.items():
            if metric_type in plot_dict:
                plot_dict[metric_type](md_file,value,metric_type)
            elif isinstance(value,(int,float,int64,str)):
                md_file.new_line(f'**{_beautify(metric_type)}** : {value}')
            elif isinstance(value,list):
                md_file.new_line(f'**{_beautify(metric_type)}**')
                if isinstance(value[0],dict):
                    add_dict_list_table(md_file,value)
                else:
                    for v in value:
                        md_file.new_line(f'* {v}')
            elif isinstance(value,dict):
                if "description" in value:
                    md_file.new_header(title=_beautify(metric_type),level=4)
                    md_file.new_paragraph(_get_description(value))
                else:
                    md_file.new_line(f'**{_beautify(metric_type)}**')
                for k,v in value.items():
                    if k in plot_dict:
                        plot_dict[k](md_file,v,metric_type)
                    elif isinstance(v,dict):
                        for k1,v1 in v.items():
                            md_file.new_line(f'* **{_beautify(str(k1))}** : {v1}')
                    elif isinstance(v,list):
                        md_file.new_line(f'\n**{_beautify(str(k))}**')
                        
                        if len(v) == 0:
                            continue
                        # Dirty, assume list of dicts
                        if isinstance(v[0],dict):
                            add_dict_list_table(md_file, v)
                        else:
                            for v1 in v:
                                md_file.new_line(f'* {_beautify(str(v1))}')
                            
                    else:
                        md_file.new_line(f'* **{_beautify(str(k))}** : {v}')


def _get_description(node):
    return node.pop('description')

def _beautify(string):
    return string.replace("_"," ").title()

def add_dict_list_table(
    md_file: MdUtils,
    records: list[dict],
    align: str = 'center',
):
    """
    Append a Markdown table to `md_file` for a list of dicts.
    - `records`: list of dicts, all with the same keys.
    - `align`: one of 'left', 'center', or 'right'.

    Cells whose values are lists will be rendered as HTML unordered lists.
    """
    if not records:
        return
    columns = list(records[0].keys())
    headers = [col.replace('_', ' ').title() for col in columns]    
    rows = []
    for record in records:
        row = []
        for col in columns:
            val = record.get(col, '')
            if isinstance(val, list):
                
                list_items = ''.join(f'<li>{item}</li>' for item in val)
                cell = f'<ul>{list_items}</ul>'
            elif isinstance(val, dict):
                list_items = ''.join(f'<li>{k}:{v}</li>' for k,v in val.items())
                cell = f'<ul>{list_items}</ul>'
            else:
                cell = str(val)
            row.append(cell)
        rows.append(row)
    flat = headers + [cell for row in rows for cell in row]
    md_file.new_table(
        columns=len(headers),
        rows=len(rows) + 1,
        text=flat,
        text_align=align,
    )
    md_file.new_paragraph('')



