from collections import defaultdict

from src.annotations_processing.formal_structs import InputSpec
from src.polirep.polirep_generator import get_polirep_per_policy


def polirep_into_inputspec(policy_path, model):
    inputspecs = []

    _, entities, relations = get_polirep_per_policy(policy_path, model)

    data_to_operation = defaultdict(list)
    for data, operation in entities['data']:
        data_to_operation[data].append(operation)

    purpose_to_operation = defaultdict(list)
    for purpose, operation in entities['purpose']:
        purpose_to_operation[purpose].append(operation)

    third_party_to_operation = defaultdict(list)
    for third_party, operation in entities['third-party']:
        third_party_to_operation[third_party].append(operation)

    data_to_purpose = defaultdict(list)
    for data, purpose in relations['purpose']:
        data_to_purpose[data].append(purpose)

    data_to_third_party = defaultdict(list)
    for data, third_party in relations['disclosure']:
        data_to_third_party[data].append(third_party)

    data_to_protection_method = defaultdict(list)
    for data, method in relations['protection']:
        data_to_protection_method[data].append(method)

    for data in data_to_operation.keys():
        purposes = []
        security_tags = []
        third_parties = []
        third_party_purposes = []
        for purpose in data_to_purpose[data]:
            for operation in purpose_to_operation:
                if operation == "first-party-collection-use":
                    purposes.append(purpose)
                elif operation == "third-party-sharing-disclosure":
                    third_party_purposes.append(purpose)

        for third_party in data_to_third_party[data]:
            for operation in third_party_to_operation:
                if operation == "third-party-sharing-disclosure":
                    third_parties.append(third_party)

        for method in data_to_protection_method[data]:
            security_tags.append(method)

        inputspecs.append(InputSpec(data, purposes, security_tags, third_parties, third_party_purposes))

    return inputspecs







if __name__ == "__main__":
    policy_path = "../data/annotations/final_benchmark/air_com_qublix_solitaireblitz"
    polirep_into_inputspec(policy_path, "OpenAI")