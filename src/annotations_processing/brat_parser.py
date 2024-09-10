import os
from collections import defaultdict


def parse_brat_file(file_path):
    annotation = {
        "entities": {},
        "relations": {},
        "events": {}
    }

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            if not parts:
                continue

            id = parts[0]
            if id.startswith('T'):  # Entity
                type_span, text = parts[1], parts[2]
                type, span = type_span.split(' ', 1)
                start, end = span.split()
                annotation["entities"][id] = [id, type, int(start), int(end), text]

            elif id.startswith('R'):  # Relation
                rel_type, args = parts[1].split(' ', 1)
                arg1, arg2 = args.split(' ')
                arg1_id = arg1.split(':')[1]
                arg2_id = arg2.split(':')[1]
                annotation["relations"][id] = [id, rel_type, arg1_id, arg2_id]

            elif id.startswith('E'):  # Event
                event_type, *args = parts[1].split(' ', 1)
                type_id = event_type.split(':')[1]
                arg_list = []
                if args:
                    for arg in args[0].split():
                        arg_name, arg_id = arg.split(':')
                        arg_list.append([arg_name, arg_id])
                annotation["events"][id] = [id, event_type.split(':')[0], type_id, arg_list]

    return annotation

def polirep_from_annotation(file_path):

    entities_raw = defaultdict(set)
    entities = defaultdict(set)
    relations_raw = defaultdict(set)
    relations = defaultdict(set)

    annotation = parse_brat_file(file_path)

    for event_id, event_data in annotation["events"].items():
        has_negation = False
        for arg in event_data[3]:
            arg_type, arg_id = arg
            if arg_type == "Polarity":
                has_negation = True
                break  # No need to continue processing this event

        if has_negation:
            continue

        if event_data[1] == "collection-use":
            data_collected_ids = []
            purpose_ids = []
            data_collector_ids = []
            third_party_collection_use = False

            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type.startswith("Data-Collected"):
                    data_collected_ids.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purpose_ids.append(arg_id)
                elif arg_type.startswith("Data-Collector"):
                    data_collector_ids.append(arg_id)

            for collector_id in data_collector_ids:
                collector_type = annotation["entities"][collector_id][1]
                if collector_type in ["Third-party-entity", "Third-party-name"]:
                    third_party_collection_use = True
                #  TODO: handle the case when there's both third-party and first-party

            data_raw = set()
            data = set()
            purposes_raw = set()
            purposes = set()

            for data_id in data_collected_ids:
                datum_raw = annotation["entities"][data_id][4]
                datum_type = annotation["entities"][data_id][1]

                # Filter out Data-General and Data-Other
                if datum_type in ["Data-general", "Data-other"]:
                    continue
                else:
                    data_raw.add(datum_raw)
                    data.add(datum_type)

            if not data_raw:  # At least one datum must be present
                continue


            for purpose_id in purpose_ids:
                purpose_raw = annotation["entities"][purpose_id][4]
                purpose_type = annotation["entities"][purpose_id][1]

                # Filter out Purpose-General and Purpose-Other
                if purpose_type in ["Purpose-general", "Purpose-other"]:
                    continue
                else:
                    purposes_raw.add(purpose_raw)
                    purposes.add(purpose_type)

            if third_party_collection_use:
                data_collectors_raw = set()

                for collector_id in data_collector_ids:
                    collector_raw = annotation["entities"][collector_id][4]
                    collector_type = annotation["entities"][collector_id][1]
                    if collector_type.startswith("Third-party-name"):
                        data_collectors_raw.add((collector_raw, "third-party-collection-use"))

                for datum_raw in data_raw:
                    entities_raw["data"].add((datum_raw, "third-party-collection-use"))
                for datum in data:
                    entities["data"].add((datum, "third-party-collection-use"))

                for purpose_raw in purposes_raw:
                    entities_raw["purpose"].add((purpose_raw, "third-party-collection-use"))
                for purpose in purposes:
                    entities["purpose"].add((purpose, "third-party-collection-use"))
                entities_raw["third-party"].update(data_collectors_raw)
                entities["third-party"].update(data_collectors_raw)

                # purpose_third-party-collection-use relations
                for datum_raw in data_raw:
                    for purpose_raw in purposes_raw:
                        # relations_raw["purpose_third-party-collection-use"].add((datum_raw, purpose_raw))
                        relations_raw["purpose"].add((datum_raw, purpose_raw))
                for datum in data:
                    for purpose in purposes:
                        # relations["purpose_third-party-collection-use"].add((datum, purpose))
                        relations["purpose"].add((datum, purpose))
            else:

                for datum_raw in data_raw:
                    entities_raw["data"].add((datum_raw, "first-party-collection-use"))
                for datum in data:
                    entities["data"].add((datum, "first-party-collection-use"))

                for purpose_raw in purposes_raw:
                    entities_raw["purpose"].add((purpose_raw, "first-party-collection-use"))
                for purpose in purposes:
                    entities["purpose"].add((purpose, "first-party-collection-use"))

                for datum_raw in data_raw:
                    for purpose_raw in purposes_raw:
                        relations_raw["purpose"].add((datum_raw, purpose_raw))
                for datum in data:
                    for purpose in purposes:
                        relations["purpose"].add((datum, purpose))

        elif event_data[1] == "third-party-sharing-disclosure":
            data_shared_ids = []
            purpose_ids = []
            data_receiver_ids = []

            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type.startswith("Data-Shared"):
                    data_shared_ids.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purpose_ids.append(arg_id)
                elif arg_type.startswith("Data-Receiver"):
                    data_receiver_ids.append(arg_id)

            data_raw = set()
            data = set()
            purposes_raw = set()
            purposes = set()
            third_parties_raw = set()
            third_parties = set()

            for data_id in data_shared_ids:
                datum_raw = annotation["entities"][data_id][4]
                datum_type = annotation["entities"][data_id][1]

                # Filter out Data-General and Data-Other
                if datum_type in ["Data-general", "Data-other"]:
                    continue
                else:
                    data_raw.add(datum_raw)
                    data.add(datum_type)

            if not data_raw:  # At least one datum must be present
                continue

            for datum_raw in data_raw:
                entities_raw["data"].add((datum_raw, "third-party-sharing-disclosure"))
            for datum in data:
                entities["data"].add((datum, "third-party-sharing-disclosure"))

            for purpose_id in purpose_ids:
                purpose_raw = annotation["entities"][purpose_id][4]
                purpose_type = annotation["entities"][purpose_id][1]

                # Filter out Purpose-General and Purpose-Other
                if purpose_type in ["Purpose-general", "Purpose-other"]:
                    continue
                else:
                    purposes_raw.add(purpose_raw)
                    purposes.add(purpose_type)

            for receiver_id in data_receiver_ids:
                third_party_raw = annotation["entities"][receiver_id][4]
                third_party = annotation["entities"][receiver_id][1]

                # Only consider concrete third parties
                if third_party.startswith("Third-party-name"):
                    third_parties_raw.add((third_party_raw, "third-party-sharing-disclosure"))

            for purpose_raw in purposes_raw:
                entities_raw["purpose"].add((purpose_raw, "third-party-sharing-disclosure"))
            for purpose in purposes:
                entities["purpose"].add((purpose, "third-party-sharing-disclosure"))
            entities_raw["third-party"].update(third_parties_raw)
            entities["third-party"].update(third_parties_raw)

            # purpose_third-party-sharing-disclosure relations
            for datum_raw in data_raw:
                for purpose_raw in purposes_raw:
                    relations_raw["purpose"].add((datum_raw, purpose_raw))
            for datum in data:
                for purpose in purposes:
                    relations["purpose"].add((datum, purpose))

            # disclosure relations
            for datum_raw in data_raw:
                for third_party_raw in third_parties_raw:
                    relations_raw["disclosure"].add((datum_raw, third_party_raw))
            for datum in data:
                for third_party in third_parties:
                    relations["disclosure"].add((datum, third_party))

        elif event_data[1] == "data-storage-retention-deletion":
            data_retained_ids = []
            purposes_ids = []

            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type.startswith("Data-Retained"):
                    data_retained_ids.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purposes_ids.append(arg_id)

            data_raw = set()
            data = set()
            purposes_raw = set()
            purposes = set()

            for data_id in data_retained_ids:
                datum_raw = annotation["entities"][data_id][4]
                datum_type = annotation["entities"][data_id][1]

                # Filter out Data-General and Data-Other
                if datum_type in ["Data-general", "Data-other"]:
                    continue
                else:
                    data_raw.add(datum_raw)
                    data.add(datum_type)

            if not data_raw:  # At least one datum must be present
                continue


            for datum_raw in data_raw:
                entities_raw["data"].add((datum_raw, "data-storage-retention-deletion"))
            for datum in data:
                entities["data"].add((datum, "data-storage-retention-deletion"))

            for purpose_id in purposes_ids:
                purpose_raw = annotation["entities"][purpose_id][4]
                purpose_type = annotation["entities"][purpose_id][1]

                # Filter out Purpose-General and Purpose-Other
                if purpose_type in ["Purpose-general", "Purpose-other"]:
                    continue
                else:
                    purposes_raw.add(purpose_raw)
                    purposes.add(purpose_type)

            #  If data is stored/retained/deleted, then it also has been collected
            for purpose_raw in purposes_raw:
                entities_raw["purpose"].add((purpose_raw, "first-party-collection-use"))
            for purpose in purposes:
                entities["purpose"].add((purpose, "first-party-collection-use"))

            for datum_raw in data_raw:
                for purpose_raw in purposes_raw:
                    # relations_raw["purpose_first-party-collection-use"].add((datum_raw, purpose_raw))
                    relations_raw["purpose"].add((datum_raw, purpose_raw))
            for datum in data:
                for purpose in purposes:
                    # relations["purpose_first-party-collection-use"].add((datum, purpose))
                    relations["purpose"].add((datum, purpose))

        elif event_data[1] == "data-security-protection":
            data_protected_ids = []
            protection_methods_ids = []

            # Iterate through the arguments of the event
            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type.startswith("Data-Protected"):
                    data_protected_ids.append(arg_id)
                elif arg_type.startswith("method"):
                    protection_methods_ids.append(arg_id)

            data_raw = set()
            data = set()
            protection_methods_raw = set()
            protection_methods = set()

            for data_id in data_protected_ids:
                datum_raw = annotation["entities"][data_id][4]
                datum_type = annotation["entities"][data_id][1]

                # Filter out Data-General and Data-Other
                if datum_type in ["Data-general", "Data-other"]:
                    continue
                else:
                    data_raw.add(datum_raw)
                    data.add(datum_type)

            if not data_raw:  # At least one datum must be present
                continue

            for datum_raw in data_raw:
                entities_raw["data"].add((datum_raw, "data-security-protection"))
            for datum in data:
                entities["data"].add((datum, "data-security-protection"))

            for method_id in protection_methods_ids:
                protection_method_raw = annotation["entities"][method_id][4]
                protection_method = annotation["entities"][method_id][1]
                protection_methods_raw.add(protection_method_raw)
                protection_methods.add(protection_method)

            entities_raw["protection-method"].update(protection_methods_raw)
            entities["protection-method"].update(protection_methods)

            # Protection relation
            for datum_raw in data_raw:
                for method_raw in protection_methods_raw:
                    relations_raw["protection"].add((datum_raw, method_raw))
            for datum in data:
                for method in protection_methods:
                    relations["protection"].add((datum, method))


    return entities_raw, entities, relations_raw, relations

def get_polirep_per_policy_from_annotation(policy_path):
    entities_raw_per_policy = defaultdict(set)
    entities_per_policy = defaultdict(set)
    relations_per_policy = defaultdict(set)

    i = 0
    while True:
        file_path = os.path.join(policy_path, f"{i}.ann")
        if not os.path.exists(file_path):
            break

        entities_raw, entities, _, relations = polirep_from_annotation(file_path)

        for key in entities_raw.keys():
            entities_raw_per_policy[key].update(entities_raw[key])
        for key in entities.keys():
            entities_per_policy[key].update(entities[key])
        for key in relations.keys():
            relations_per_policy[key].update(relations[key])

        i += 1

    return entities_raw_per_policy, entities_per_policy, relations_per_policy


def extract_subsume_relations(annotation):
    subsume_relations = {}

    for relation_id, relation_data in annotation["relations"].items():
        # Check if the relation type is "SUBSUME"
        if relation_data[1] == "SUBSUME":
            parent_id = relation_data[2]  # arg1_id is the parent (more general term)
            child_id = relation_data[3]   # arg2_id is the child (more specific term)

            # If the parent is not in the dictionary, add it with an empty list
            if parent_id not in subsume_relations:
                subsume_relations[parent_id] = []

            # Add the child to the list of the parent
            subsume_relations[parent_id].append(child_id)

    return subsume_relations

def analyze_first_party_collection_use(annotation):
    event_triples = []

    for event_id, event_data in annotation["events"].items():
        # Check if the event type is "first-party-collection-use"
        if event_data[1] == "first-party-collection-use":
            data_collected = []
            purposes = []
            conditions = []
            has_negation = False

            # Iterate through the arguments of the event
            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type == "Polarity":
                    has_negation = True
                    break  # No need to continue processing this event
                elif arg_type.startswith("Data-Collected"):
                    data_collected.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purposes.append(arg_id)
                elif arg_type.startswith("Condition-Argument"):
                    conditions.append(arg_id)

            # If the event has a Negation argument, skip it
            if has_negation:
                continue

            # If no purposes are found, add None to ensure at least one iteration
            purposes = purposes if purposes else [None]

            # Generate all possible combinations of Data-Collected and Purpose
            for data_id in data_collected:
                for purpose_id in purposes:
                    event_triples.append((data_id, purpose_id, conditions))

    return event_triples

def analyze_third_party_sharing_disclosure(annotation):
    event_tuples = []

    for event_id, event_data in annotation["events"].items():
        # Check if the event type is "third-party-sharing-disclosure"
        if event_data[1] == "third-party-sharing-disclosure":
            data_shared = []
            purposes = []
            data_receivers = []
            conditions = []
            has_polarity = False

            # Iterate through the arguments of the event
            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type == "Polarity":
                    has_polarity = True
                    break  # No need to continue processing this event
                elif arg_type.startswith("Data-Shared"):
                    data_shared.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purposes.append(arg_id)
                elif arg_type.startswith("Data-Receiver"):
                    data_receivers.append(arg_id)
                elif arg_type.startswith("Condition-Argument"):
                    conditions.append(arg_id)

            # If the event has a Polarity argument, skip it
            if has_polarity:
                continue

            # If no purposes are found, add None to ensure at least one iteration
            purposes = purposes if purposes else [None]
            # If no data receivers are found, add None to ensure at least one iteration
            data_receivers = data_receivers if data_receivers else [None]

            # Generate all possible combinations of Data-Shared, Purpose, and Data-Receiver
            for data_id in data_shared:
                for purpose_id in purposes:
                    for receiver_id in data_receivers:
                        event_tuples.append((data_id, purpose_id, receiver_id, conditions))

    return event_tuples

def analyze_data_storage_retention_deletion(annotation):
    event_triples = []

    for event_id, event_data in annotation["events"].items():
        # Check if the event type is "first-party-collection-use"
        if event_data[1] == "data-storage-retention-deletion":
            data_collected = []
            purposes = []
            conditions = []
            has_negation = False

            # Iterate through the arguments of the event
            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type == "Polarity":
                    has_negation = True
                    break  # No need to continue processing this event
                elif arg_type.startswith("Data-Retained"):
                    data_collected.append(arg_id)
                elif arg_type.startswith("Purpose-Argument"):
                    purposes.append(arg_id)
                elif arg_type.startswith("Condition-Argument"):
                    conditions.append(arg_id)

            # If the event has a Negation argument, skip it
            if has_negation:
                continue

            # If no purposes are found, add None to ensure at least one iteration
            purposes = purposes if purposes else [None]

            # Generate all possible combinations of Data-Collected and Purpose
            for data_id in data_collected:
                for purpose_id in purposes:
                    event_triples.append((data_id, purpose_id, conditions))

    return event_triples

def analyze_data_security_protection(annotation):
    event_triples = []

    for event_id, event_data in annotation["events"].items():
        if event_data[1] == "data-security-protection":
            data_protected = []
            methods = []
            conditions = []
            has_polarity = False
            for arg in event_data[3]:
                arg_type, arg_id = arg
                if arg_type == "Polarity":
                    has_polarity = True
                    break  # No need to continue processing this event
                elif arg_type.startswith("Data-Protected"):
                    data_protected.append(arg_id)
                elif arg_type.startswith("method"):
                    methods.append(arg_id)
                elif arg_type.startswith("Condition-Argument"):
                    conditions.append(arg_id)

            # If the event has a Polarity argument, skip it
            if has_polarity:
                continue

            # If no methods are found, add None to ensure at least one iteration
            methods = methods if methods else [None]

            # Generate all possible combinations of Data-Protected and Method
            for data_id in data_protected:
                for method_id in methods:
                    event_triples.append((data_id, method_id, conditions))

    return event_triples


if __name__ == "__main__":
    # file_path = "../../data/annotations/final_benchmark/9gag/3.ann"
    file_path = "../../data/annotations/final_benchmark/air_com_qublix_solitaireblitz/3.ann"
    entities_raw, entities, relations_raw, relations = polirep_from_annotation(file_path)

    print(entities_raw)
    print(entities)
    print(relations_raw)
    print(relations)