import os
from collections import defaultdict

from src.polirep.categories_mapper_struct import get_purpose_categories_for_list, get_data_categories_for_list, \
    get_protection_method_categories_for_list
from src.polirep.annotators.relations_annotator import get_relations_per_segment


def get_entities_and_relations_per_segment(segment_file_path, model):
    entities_raw_with_ids, relations_raw = get_relations_per_segment(segment_file_path, model)

    entities = defaultdict(set)

    data_raw = entities_raw_with_ids["data"]
    data_texts = [triple[1] for triple in data_raw]
    data_categories_per_segment_raw = get_data_categories_for_list(data_texts, model)
    data_categories_dict = {item['phrase']: item['category'] for item in data_categories_per_segment_raw}

    for id, text, operation in data_raw:
        if text in data_categories_dict.keys(): # TODO: change this
            entities["data"].add((id, data_categories_dict[text], operation))

    purpose_raw = entities_raw_with_ids["purpose"]
    purpose_texts = [triple[1] for triple in purpose_raw]
    purpose_categories_per_segment_raw = get_purpose_categories_for_list(purpose_texts, model)
    purpose_categories_dict = {item['phrase']: item['category'] for item in purpose_categories_per_segment_raw}

    for id, text, operation in purpose_raw:
        if text in purpose_categories_dict.keys():
            entities["purpose"].add((id, purpose_categories_dict[text], operation))

    entities["third-party"] = entities_raw_with_ids["third-party"]

    methods_raw = entities_raw_with_ids["protection-method"]
    methods_texts = [pair[1] for pair in methods_raw]
    methods_categories_per_segment_raw = get_protection_method_categories_for_list(methods_texts, model)
    methods_categories_dict = {item['phrase']: item['category'] for item in methods_categories_per_segment_raw}

    for id, text in methods_raw:
        if text in methods_categories_dict.keys():
            entities["protection-method"].add((id, methods_categories_dict[text]))

    relations = defaultdict(set)

    data_dict = {id: type for id, type, _ in entities["data"]}
    purpose_dict = {id: type for id, type, _ in entities["purpose"]}
    third_party_dict = {id: type for id, type, _ in entities["third-party"]}
    methods_dict = {id: type for id, type in entities["protection-method"]}


    for data_id, purpose_id in relations_raw["purpose"]:
        if data_id in data_dict.keys() and purpose_id in purpose_dict.keys():
            relations["purpose"].add((data_dict[data_id], purpose_dict[purpose_id]))
    for data_id, third_party_id in relations_raw["disclosure"]:
        if data_id in data_dict.keys() and third_party_id in third_party_dict.keys():
            relations["disclosure"].add((data_dict[data_id], third_party_dict[third_party_id]))
    for data_id, method_id in relations_raw["protection"]:
        if data_id in data_dict.keys() and method_id in methods_dict.keys():
            relations["protection"].add((data_dict[data_id], methods_dict[method_id]))

    # Get rid of Ids:
    entities_raw = defaultdict(set)
    for id, text, operation in entities_raw_with_ids["data"]:
        entities_raw["data"].add((text, operation))
    for id, text, operation in entities_raw_with_ids["purpose"]:
        entities_raw["purpose"].add((text, operation))
    for id, text, operation in entities_raw_with_ids["third-party"]:
        entities_raw["third-party"].add((text, operation))
    for id, text in entities_raw_with_ids["protection-method"]:
        entities_raw["protection-method"].add(text)

    entities_cleaned = defaultdict(set)
    for id, category, operation in entities["data"]:
        entities_cleaned["data"].add((category, operation))
    for id, category, operation in entities["purpose"]:
        entities_cleaned["purpose"].add((category, operation))
    for id, text, operation in entities["third-party"]:
        entities_cleaned["third-party"].add((text, operation))
    for id, category in entities["protection-method"]:
        entities_cleaned["protection-method"].add(category)

    return entities_raw, entities_cleaned, relations

def get_polirep_per_policy(policy_path, model):
    entities_raw_per_policy = defaultdict(set)
    entities_per_policy = defaultdict(set)
    relations_per_policy = defaultdict(set)

    i = 0
    while True:
        file_path = os.path.join(policy_path, f"{i}.ann")
        if not os.path.exists(file_path):
            break

        entities_raw, entities, relations = get_entities_and_relations_per_segment(file_path, model)


        for key in entities_raw.keys():
            entities_raw_per_policy[key].update(entities_raw[key])
        for key in entities.keys():
            entities_per_policy[key].update(entities[key])
        for key in relations.keys():
            relations_per_policy[key].update(relations[key])

        i += 1

    return entities_raw_per_policy, entities_per_policy, relations_per_policy


if __name__ == "__main__":
    policy_path = "../../data/annotations/final_benchmark/air_com_qublix_solitaireblitz"
    entities_raw, entities, relations = get_polirep_per_policy(policy_path, "OpenAI")

    print(entities_raw)
    print(entities)
    print(relations)
