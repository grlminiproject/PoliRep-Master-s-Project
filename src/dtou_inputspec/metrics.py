import os
from collections import defaultdict

from src.annotations_processing.annotation_into_inputspec import annotation_into_inputspec
from src.dtou_inputspec.inputspec_from_polirep import polirep_into_inputspec


# def compute_metrics(policy_path, model):
#     predicted = polirep_into_inputspec(policy_path, model)
#     annotated = annotation_into_inputspec(policy_path)


def compute_metrics(policies_folder, model):
    all_true_positives = 0
    all_false_positives = 0
    all_false_negatives = 0

    for policy_file in os.listdir(policies_folder):
        policy_path = os.path.join(policies_folder, policy_file)
        predicted = polirep_into_inputspec(policy_path, model)
        annotated = annotation_into_inputspec(policy_path)

        true_positives, false_positives, false_negatives = compare_inputspecs(predicted, annotated)

        all_true_positives += true_positives
        all_false_positives += false_positives
        all_false_negatives += false_negatives

    precision = calculate_metric(all_true_positives, all_false_positives)
    recall = calculate_metric(all_true_positives, all_false_negatives)
    f1 = calculate_f1(precision, recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def compare_inputspecs(predicted, annotated):
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    pred_set = set((spec.data, tuple(spec.purposes), tuple(spec.security_tags),
                    tuple(spec.third_parties), tuple(spec.third_party_purposes))
                   for spec in predicted)
    anno_set = set((spec.data, tuple(spec.purposes), tuple(spec.security_tags),
                    tuple(spec.third_parties), tuple(spec.third_party_purposes))
                   for spec in annotated)

    true_positives = len(pred_set & anno_set)
    false_positives = len(pred_set - anno_set)
    false_negatives = len(anno_set - pred_set)

    return true_positives, false_positives, false_negatives


def calculate_metric(true_positives, false_counts):
    return true_positives / (true_positives + false_counts) if (true_positives + false_counts) > 0 else 0.0


def calculate_f1(precision, recall):
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

if __name__ == "__main__":
    # metrics = compute_metrics("../../data/annotations/fully_annotated_benchmark", "OpenAI")
    metrics = compute_metrics("../../data/annotations/fully_annotated_benchmark", "Anthropic")
    # metrics = compute_metrics("../../data/annotations/will_be_deleted", "OpenAI")
    print(metrics)

