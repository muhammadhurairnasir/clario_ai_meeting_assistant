"""
services/evaluation.py
-----------------------
ROUGE and F1 evaluation utilities for summarisation and task detection quality.
Extracted from Clario Project notebook (cells 118–119).
"""

import json
import os
from typing import List, Dict, Any


# ── ROUGE Evaluation ───────────────────────────────────────────────────────────

def evaluate_rouge(
    ai_summary: str,
    reference_summary: str,
    use_stemmer: bool = True,
) -> Dict[str, Any]:
    """
    Compute ROUGE-1, ROUGE-2, and ROUGE-L scores between *ai_summary* and
    *reference_summary*.

    Parameters
    ----------
    ai_summary        : Machine-generated summary to evaluate.
    reference_summary : Human-written reference / gold standard.
    use_stemmer       : Whether to use stemming when computing ROUGE.

    Returns
    -------
    dict with keys 'rouge1', 'rouge2', 'rougeL', 'average_f'
        Each sub-dict contains 'precision', 'recall', 'fmeasure'.
    """
    from rouge_score import rouge_scorer as _rouge_scorer

    scorer = _rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=use_stemmer,
    )
    scores = scorer.score(reference_summary, ai_summary)

    avg_f = sum(s.fmeasure for s in scores.values()) / 3

    results = {
        "rouge1": {
            "precision": round(scores["rouge1"].precision, 4),
            "recall":    round(scores["rouge1"].recall,    4),
            "fmeasure":  round(scores["rouge1"].fmeasure,  4),
        },
        "rouge2": {
            "precision": round(scores["rouge2"].precision, 4),
            "recall":    round(scores["rouge2"].recall,    4),
            "fmeasure":  round(scores["rouge2"].fmeasure,  4),
        },
        "rougeL": {
            "precision": round(scores["rougeL"].precision, 4),
            "recall":    round(scores["rougeL"].recall,    4),
            "fmeasure":  round(scores["rougeL"].fmeasure,  4),
        },
        "average_f": round(avg_f, 4),
    }

    # Human-readable rating
    if avg_f >= 0.5:
        results["rating"] = "GOOD"
    elif avg_f >= 0.3:
        results["rating"] = "ACCEPTABLE"
    else:
        results["rating"] = "NEEDS_IMPROVEMENT"

    return results


def print_rouge_report(rouge_results: Dict[str, Any]) -> None:
    """Pretty-print a ROUGE results dict to stdout."""
    print("=" * 60)
    print("📊 ROUGE SCORES:")
    print("=" * 60)
    for metric in ("rouge1", "rouge2", "rougeL"):
        s = rouge_results[metric]
        bar_len = int(s["fmeasure"] * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"\n{metric.upper()}:")
        print(f"  Precision : {s['precision']:.4f}")
        print(f"  Recall    : {s['recall']:.4f}")
        print(f"  F-Measure : {s['fmeasure']:.4f}")
        print(f"  [{bar}] {s['fmeasure']:.2%}")
    avg = rouge_results["average_f"]
    print(f"\n📈 Average F-Measure: {avg:.4f}")
    rating = rouge_results.get("rating", "")
    print(f"Rating: {rating}")


# ── F1 Evaluation ──────────────────────────────────────────────────────────────

def evaluate_f1(
    detected_tasks: List[Dict[str, Any]],
    ground_truth_tasks: List[str],
    overlap_threshold: float = 0.4,
) -> Dict[str, Any]:
    """
    Compute Precision, Recall, and F1 for a task-detection run.

    Matching strategy: a detected task and a ground-truth task are considered a
    match when the word-overlap ratio exceeds *overlap_threshold*.

    Parameters
    ----------
    detected_tasks     : List of task dicts (must have a 'description' key).
    ground_truth_tasks : List of ground-truth task description strings.
    overlap_threshold  : Fraction of words that must overlap (default 0.4 = 40 %).

    Returns
    -------
    dict with keys: true_positives, false_positives, false_negatives,
                    precision, recall, f1_score, rating
    """
    detected_descriptions = [t.get("description", "") for t in detected_tasks]

    true_positives = 0
    false_negatives = 0

    for gt_task in ground_truth_tasks:
        gt_words = set(gt_task.lower().split())
        matched = False
        for det_desc in detected_descriptions:
            det_words = set(det_desc.lower().split())
            overlap = len(gt_words & det_words)
            ratio = overlap / max(len(gt_words), 1)
            if ratio > overlap_threshold:
                matched = True
                break
        if matched:
            true_positives += 1
        else:
            false_negatives += 1

    false_positives = 0
    for det_desc in detected_descriptions:
        det_words = set(det_desc.lower().split())
        matched = False
        for gt_task in ground_truth_tasks:
            gt_words = set(gt_task.lower().split())
            overlap = len(gt_words & det_words)
            ratio = overlap / max(len(det_words), 1)
            if ratio > overlap_threshold:
                matched = True
                break
        if not matched:
            false_positives += 1

    precision = true_positives / max(true_positives + false_positives, 1)
    recall    = true_positives / max(true_positives + false_negatives, 1)
    f1        = 2 * (precision * recall) / max(precision + recall, 1e-9)

    results = {
        "true_positives":  true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision":       round(precision, 4),
        "recall":          round(recall,    4),
        "f1_score":        round(f1,        4),
    }

    if f1 >= 0.7:
        results["rating"] = "GOOD"
    elif f1 >= 0.5:
        results["rating"] = "ACCEPTABLE"
    else:
        results["rating"] = "NEEDS_IMPROVEMENT"

    return results


def print_f1_report(f1_results: Dict[str, Any]) -> None:
    """Pretty-print an F1 results dict to stdout."""
    print("=" * 60)
    print("📊 F1 EVALUATION RESULTS:")
    print("=" * 60)
    print(f"\n  True Positives  (correctly found tasks) : {f1_results['true_positives']}")
    print(f"  False Positives (wrongly detected)      : {f1_results['false_positives']}")
    print(f"  False Negatives (missed real tasks)     : {f1_results['false_negatives']}")
    p = f1_results["precision"]
    r = f1_results["recall"]
    f = f1_results["f1_score"]
    p_bar = "█" * int(p * 30) + "░" * (30 - int(p * 30))
    r_bar = "█" * int(r * 30) + "░" * (30 - int(r * 30))
    f_bar = "█" * int(f * 30) + "░" * (30 - int(f * 30))
    print(f"\n  Precision : {p:.4f} ({p:.2%})")
    print(f"  Recall    : {r:.4f} ({r:.2%})")
    print(f"  F1 Score  : {f:.4f} ({f:.2%})")
    print(f"\n  Precision [{p_bar}] {p:.2%}")
    print(f"  Recall    [{r_bar}] {r:.2%}")
    print(f"  F1 Score  [{f_bar}] {f:.2%}")
    print(f"\nRating: {f1_results.get('rating', '')}")


# ── Persistence helpers ────────────────────────────────────────────────────────

def save_evaluation(results: Dict[str, Any], output_path: str) -> None:
    """Save evaluation results dict to a JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=4)
    print(f"💾 Evaluation scores saved to: {output_path}")
