import argparse
import os
import sys
from collections import defaultdict

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.annotations_processing.brat_parser import get_polirep_per_policy_from_annotation
from src.polirep.polirep_generator import get_polirep_per_policy

def compute_precision_recall_f1(policy_path, model):
    entities_raw_predicted, entities_predicted, relations_predicted = get_polirep_per_policy(policy_path, model)
    entities_raw_annotated, entities_annotated, relations_annotated = get_polirep_per_policy_from_annotation(
        policy_path)



    def preprocess_entities(entities):
        processed = defaultdict(set)
        for key, value_set in entities.items():
            if key in ['data', 'purpose', 'third-party']:
                processed[key] = {v[0] for v in value_set}
            else:
                processed[key] = value_set
        return processed

    def calculate_metrics(predicted, annotated):
        if not annotated:
            return 1.0, 1.0, 1.0  # Perfect precision, recall, and F1 when annotated set is empty

        true_positives = len(predicted.intersection(annotated))
        false_positives = len(predicted - annotated)
        false_negatives = len(annotated - predicted)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        # Calculate F1 score
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return precision, recall, f1

    results = defaultdict(lambda: defaultdict(dict))

    # Preprocess entities
    entities_raw_predicted_processed = preprocess_entities(entities_raw_predicted)
    entities_predicted_processed = preprocess_entities(entities_predicted)
    entities_raw_annotated_processed = preprocess_entities(entities_raw_annotated)
    entities_annotated_processed = preprocess_entities(entities_annotated)

    # Calculate metrics for entities_raw
    for key in set(entities_raw_predicted_processed.keys()).union(entities_raw_annotated_processed.keys()):
        precision, recall, f1 = calculate_metrics(
            entities_raw_predicted_processed.get(key, set()),
            entities_raw_annotated_processed.get(key, set())
        )
        results['entities_raw'][key] = {'precision': precision, 'recall': recall, 'f1': f1}

    # Calculate metrics for entities
    for key in set(entities_predicted_processed.keys()).union(entities_annotated_processed.keys()):
        precision, recall, f1 = calculate_metrics(
            entities_predicted_processed.get(key, set()),
            entities_annotated_processed.get(key, set())
        )
        results['entities'][key] = {'precision': precision, 'recall': recall, 'f1': f1}

    # Calculate metrics for relations
    for key in set(relations_predicted.keys()).union(relations_annotated.keys()):
        precision, recall, f1 = calculate_metrics(
            relations_predicted.get(key, set()),
            relations_annotated.get(key, set())
        )
        results['relations'][key] = {'precision': precision, 'recall': recall, 'f1': f1}

    return dict(results)


def compute_overall_precision_recall_f1(policies_dir, model):
    overall_results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for policy_folder in os.listdir(policies_dir):
        print(policy_folder)
        policy_path = os.path.join(policies_dir, policy_folder)
        if os.path.isdir(policy_path):
            policy_results = compute_precision_recall_f1(policy_path, model)

            for category in policy_results:
                for key in policy_results[category]:
                    overall_results[category][key]['precision'].append(policy_results[category][key]['precision'])
                    overall_results[category][key]['recall'].append(policy_results[category][key]['recall'])
                    overall_results[category][key]['f1'].append(policy_results[category][key]['f1'])

    # Calculate average precision, recall, and F1 score
    final_results = defaultdict(lambda: defaultdict(dict))
    for category in overall_results:
        for key in overall_results[category]:
            precision_values = overall_results[category][key]['precision']
            recall_values = overall_results[category][key]['recall']
            f1_values = overall_results[category][key]['f1']

            final_results[category][key]['precision'] = sum(precision_values) / len(
                precision_values) if precision_values else 0
            final_results[category][key]['recall'] = sum(recall_values) / len(recall_values) if recall_values else 0
            final_results[category][key]['f1'] = sum(f1_values) / len(f1_values) if f1_values else 0

    return dict(final_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute overall precision, recall, and F1 score for policies.")
    parser.add_argument("policies_directory", help="Path to the directory containing policy folders")
    parser.add_argument("model", help="Model name (e.g., 'Anthropic')")
    args = parser.parse_args()


    # policies_directory = "../data/annotations/fully_annotated_benchmark"
    # model = "Anthropic"

    # overall_results = compute_overall_precision_recall_f1(policies_directory, model)
    overall_results = compute_overall_precision_recall_f1(args.policies_directory, args.model)

    # Print overall results
    for category in overall_results:
        print(f"\n{category.upper()}:")
        for key in overall_results[category]:
            precision = overall_results[category][key]['precision']
            recall = overall_results[category][key]['recall']
            f1 = overall_results[category][key]['f1']
            print(f"  {key}:")
            print(f"    Precision: {precision:.4f}")
            print(f"    Recall: {recall:.4f}")
            print(f"    F1 Score: {f1:.4f}")