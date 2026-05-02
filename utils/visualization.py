"""
utils/visualization.py
-----------------------
Knowledge graph and chart generation utilities.
Extracted from Clario Project notebook (cell 115).
"""

import os
import json
from typing import List, Dict, Any, Optional


def build_knowledge_graph(
    tasks: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    """
    Build and render a knowledge-graph visualisation of the detected tasks.

    Creates a directed graph where:
      - Each task node is labelled with a short description snippet.
      - Person nodes are connected to the tasks assigned to them.
      - Date nodes are attached where a due_date was extracted.

    Parameters
    ----------
    tasks       : List of task dicts (description, assigned_to, due_date, keyword).
    output_path : If given, save the PNG to this path.  Defaults to
                  ``data/graphs/knowledge_graph.png`` relative to the project root.
    show        : Whether to call ``plt.show()`` after rendering (interactive use).

    Returns
    -------
    str – Absolute path of the saved image, or an empty string if saving was
          skipped and ``show=False``.
    """
    try:
        import networkx as nx
        import matplotlib
        matplotlib.use("Agg")           # non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "visualization.py requires 'networkx' and 'matplotlib'. "
            f"Install them first.  Original error: {exc}"
        )

    # ── Build graph ────────────────────────────────────────────────────────────
    G = nx.DiGraph()

    MEETING_NODE = "Meeting"
    G.add_node(MEETING_NODE, type="meeting")

    for task in tasks:
        desc    = task.get("description", "")
        person  = task.get("assigned_to", "Unknown")
        due     = task.get("due_date",    "Not specified")
        keyword = task.get("keyword",     "")
        task_id = f"Task-{task.get('id', len(G.nodes))}"

        # Shorten label
        label = desc[:50] + ("…" if len(desc) > 50 else "")
        G.add_node(task_id, type="task", label=label, keyword=keyword)
        G.add_edge(MEETING_NODE, task_id)

        if person != "Unknown":
            G.add_node(person, type="person")
            G.add_edge(task_id, person)

        if due != "Not specified":
            due_node = f" {due}"
            G.add_node(due_node, type="date")
            G.add_edge(task_id, due_node)

    # ── Colour map ─────────────────────────────────────────────────────────────
    color_map = []
    for node in G.nodes:
        node_type = G.nodes[node].get("type", "")
        if node_type == "meeting":
            color_map.append("#3B4A6B")     # blue
        elif node_type == "task":
            color_map.append("#C48B47")     # amber
        elif node_type == "person":
            color_map.append("#4A7C59")     # green
        else:                               # date
            color_map.append("#A64444")     # red

    # ── Layout and draw ────────────────────────────────────────────────────────
    print("Building knowledge graph …")
    pos = nx.spring_layout(G, seed=42, k=2.0)

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=1500, ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, ax=ax)

    labels = {n: G.nodes[n].get("label", n) for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="#EAECEF", ax=ax)

    ax.set_title("️ Clario Knowledge Graph", fontsize=14)
    ax.axis("off")
    plt.tight_layout()

    # ── Save ───────────────────────────────────────────────────────────────────
    saved_path = ""
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        saved_path = os.path.abspath(output_path)
        print(f" Knowledge graph saved to: {saved_path}")

    if show:
        plt.show()

    plt.close(fig)
    return saved_path


def generate_assignee_bar_chart(
    tasks: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    """
    Generate a professional bar chart showing tasks per person.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(f"visualization.py requires 'matplotlib'. Error: {exc}")

    by_person = {}
    for task in tasks:
        person = task.get("assigned_to", "Unknown")
        by_person[person] = by_person.get(person, 0) + 1

    if not by_person:
        return ""

    names = list(by_person.keys())
    counts = list(by_person.values())

    # Styling
    if 'seaborn-v0_8-whitegrid' in plt.style.available:
        plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Beautiful colors
    colors = ['#3B4A6B', '#4A7C59', '#C48B47', '#A64444', '#7A7A85', '#4A6D7C']
    bar_colors = [colors[i % len(colors)] for i in range(len(names))]
    
    bars = ax.bar(names, counts, color=bar_colors, edgecolor='none', width=0.6, alpha=0.85)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', color='#EAECEF')

    ax.set_ylabel("Number of Tasks", fontweight='bold', color='#B0B4BE')
    ax.set_title("Tasks by Assignee", fontsize=14, fontweight='bold', pad=15, color='#EAECEF')
    
    # Remove top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#3A3D45')
    ax.spines['bottom'].set_color('#3A3D45')
    
    plt.xticks(rotation=45 if len(names) > 4 else 0, ha='right' if len(names) > 4 else 'center')
    ax.tick_params(colors='#B0B4BE')
    plt.tight_layout()

    saved_path = ""
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight", transparent=True)
        saved_path = os.path.abspath(output_path)

    if show:
        plt.show()

    plt.close(fig)
    return saved_path


def generate_priority_donut_chart(
    tasks: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    """
    Generate a professional donut chart showing task priority distribution.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(f"visualization.py requires 'matplotlib'. Error: {exc}")

    by_priority = {"High": 0, "Medium": 0, "Low": 0}
    for task in tasks:
        prio = task.get("priority", "Low")
        if prio in by_priority:
            by_priority[prio] += 1
        else:
            by_priority["Low"] += 1

    # Filter out zero counts
    filtered_priority = {k: v for k, v in by_priority.items() if v > 0}

    if not filtered_priority:
        return ""

    labels = list(filtered_priority.keys())
    sizes = list(filtered_priority.values())

    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Priority semantic colors
    color_map = {"High": "#A64444", "Medium": "#C48B47", "Low": "#4A7C59"}
    pie_colors = [color_map[l] for l in labels]
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%',
        startangle=90, colors=pie_colors, 
        wedgeprops=dict(width=0.4, edgecolor='#12151C', linewidth=2),
        textprops=dict(color="w", fontweight='bold', fontsize=9)
    )
    
    # Improve label readability
    for text in texts:
        text.set_color('#EAECEF')
        text.set_fontsize(10)

    ax.set_title("Task Priority Distribution", fontsize=14, fontweight='bold', pad=15, color='#EAECEF')
    
    plt.tight_layout()

    saved_path = ""
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight", transparent=True)
        saved_path = os.path.abspath(output_path)

    if show:
        plt.show()

    plt.close(fig)
    return saved_path


def generate_status_pie_chart(
    tasks: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    """
    Generate a professional pie chart showing pending vs completed tasks.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(f"visualization.py requires 'matplotlib'. Error: {exc}")

    by_status = {"pending": 0, "completed": 0}
    for task in tasks:
        st = task.get("status", "pending")
        if st in by_status:
            by_status[st] += 1
        else:
            by_status["pending"] += 1

    filtered_status = {k: v for k, v in by_status.items() if v > 0}
    if not filtered_status:
        return ""

    labels = ["Completed" if k == "completed" else "Pending" for k in filtered_status.keys()]
    sizes = list(filtered_status.values())

    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Semantic colors for status
    color_map = {"Completed": "#4A7C59", "Pending": "#C48B47"}
    pie_colors = [color_map.get(l, "#7A7A85") for l in labels]
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%',
        startangle=90, colors=pie_colors, 
        wedgeprops=dict(width=0.6, edgecolor='#12151C', linewidth=2),
        textprops=dict(color="w", fontweight='bold', fontsize=9)
    )
    
    for text in texts:
        text.set_color('#EAECEF')
        text.set_fontsize(10)

    ax.set_title("Task Completion Status", fontsize=14, fontweight='bold', pad=15, color='#EAECEF')
    
    plt.tight_layout()

    saved_path = ""
    if output_path:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight", transparent=True)
        saved_path = os.path.abspath(output_path)

    if show:
        plt.show()

    plt.close(fig)
    return saved_path
