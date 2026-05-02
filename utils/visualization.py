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
            color_map.append("#4A90D9")     # blue
        elif node_type == "task":
            color_map.append("#E8A838")     # amber
        elif node_type == "person":
            color_map.append("#5CB85C")     # green
        else:                               # date
            color_map.append("#D9534F")     # red

    # ── Layout and draw ────────────────────────────────────────────────────────
    print("Building knowledge graph …")
    pos = nx.spring_layout(G, seed=42, k=2.0)

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=1500, ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, ax=ax)

    labels = {n: G.nodes[n].get("label", n) for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, ax=ax)

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


def generate_task_bar_chart(
    stats: Dict[str, Any],
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    """
    Generate a bar chart that shows the number of tasks per person.

    Parameters
    ----------
    stats       : Dict produced by ``task_detection.get_task_summary()``.
                  Expected keys: ``by_person`` (dict name→count), ``unassigned_count``.
    output_path : Save destination for the PNG.
    show        : Show interactively.

    Returns
    -------
    str – Path of saved image or empty string.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "visualization.py requires 'matplotlib'. "
            f"Install it first.  Original error: {exc}"
        )

    by_person     = stats.get("by_person", {})
    unassigned    = stats.get("unassigned_count", 0)
    if unassigned:
        by_person["Unknown"] = unassigned

    if not by_person:
        print("No task data available for chart.")
        return ""

    names  = list(by_person.keys())
    counts = list(by_person.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(names, counts, color="#4A90D9")
    ax.set_xlabel("Assignee")
    ax.set_ylabel("Number of Tasks")
    ax.set_title("Tasks per Person")
    plt.tight_layout()

    saved_path = ""
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        saved_path = os.path.abspath(output_path)
        print(f" Bar chart saved to: {saved_path}")

    if show:
        plt.show()

    plt.close(fig)
    return saved_path
