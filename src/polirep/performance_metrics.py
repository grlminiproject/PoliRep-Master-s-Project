import os

from src.annotations_processing.brat_parser import parse_brat_file
from src.polirep.categories_mapper_struct import get_data_categories_for_list
from src.polirep.annotators.entities_annotator import get_data_entities_for_policies

data_set = set([
    "Data-aggregated-nonidentifiable", "Data-cookies-web-beacons-and-other-technologies",
    "Data-user-online-activities-profiles", "Data-location", "Data-computer-device", "Data-finance",
    "Data-contact", "Data-demographic", "Data-other", "Internal", "Authenticating", "Password", "PINCode",
    "SecretText", "KnowledgeBelief", "PhilosophicalBelief", "ReligiousBelief", "Thought", "Preference",
    "Favorite", "FavoriteColor", "FavoriteFood", "FavoriteMusic", "Intention", "Interest", "Dislike",
    "Like", "Opinion", "PrivacyPreference", "External", "Behavioral", "Attitude", "AuthenticationHistory",
    "BrowsingBehavior", "BrowserHistory", "BrowsingReferral", "CallLog", "Demeanor", "LinkClicked",
    "Personality", "Reliability", "ServiceConsumptionBehavior", "TVViewingBehavior", "AdInteractionBehavior",
    "Citizenship", "Demographic", "Geographic", "IncomeBracket", "PhysicalTrait", "Ethnicity", "EthnicOrigin",
    "Race", "Identifying", "Biometric", "FacialPrint", "Fingerprint", "Retina", "Name", "OfficialID",
    "Passport", "Picture", "UID", "Username", "VehicleLicense", "VehicleLicenseNumber",
    "VehicleLicenseRegistration", "Language", "Accent", "Dialect", "MedicalHealth", "BloodType",
    "Disability", "DNACode", "DrugTestResult", "Health", "Genetic", "MentalHealth", "PhysicalHealth",
    "HealthHistory", "FamilyHealthHistory", "IndividualHealthHistory", "HealthRecord", "Prescription",
    "Nationality", "PersonalDocuments", "PhysicalCharacteristic", "Age", "AgeRange", "AgeExact",
    "BirthDate", "Gender", "HairColor", "Height", "Piercing", "SkinTone", "Tattoo", "Weight", "Sexual",
    "Fetish", "Proclivity", "SexualHistory", "SexualPreference", "Vehicle", "VehicleUsage", "Financial",
    "FinancialAccount", "AccountIdentifier", "FinancialAccountNumber", "BankAccount", "PaymentCard",
    "PaymentCardExpiry", "PaymentCardNumber", "CreditCardNumber", "FinancialStatus", "Insurance",
    "Ownership", "CarOwned", "HouseOwned", "ApartmentOwned", "PersonalPossession", "Transactional",
    "Credit", "CreditCapacity", "CreditRecord", "CreditStanding", "CreditWorthiness", "CreditScore",
    "Income", "LoanRecord", "Purchase", "PurchasesAndSpendingHabit", "Sale", "Tax", "Transaction",
    "Historical", "LifeHistory", "Social", "Communication", "EmailContent", "SocialMedia",
    "PubliclyAvailableSocialMedia", "SocialMediaCommunication", "VoiceCommunicationRecording",
    "VoiceMail", "Criminal", "CriminalCharge", "CriminalConviction", "CriminalOffense", "CriminalPardon",
    "Family", "FamilyStructure", "Divorce", "Marriage", "Offspring", "Parent", "Sibling", "Relationship",
    "Professional", "DisciplinaryAction", "Education", "EducationExperience", "EducationQualification",
    "EmploymentHistory", "CurrentEmployment", "PastEmployment", "Job", "PerformanceAtWork",
    "ProfessionalCertification", "ProfessionalEvaluation", "ProfessionalInterview", "Reference",
    "Salary", "School", "WorkEnvironment", "WorkHistory", "PublicLife", "Character",
    "CommunicationsMetadata", "GeneralReputation", "Interaction", "MaritalStatus", "PoliticalAffiliation",
    "PoliticalOpinion", "Religion", "SocialStatus", "SocialNetwork", "Acquantaince", "Association",
    "Connection", "Friend", "GroupMembership", "TradeUnionMembership", "Tracking", "Contact",
    "EmailAddress", "EmailAddressPersonal", "EmailAddressWork", "TelephoneNumber", "DeviceBased",
    "BrowserFingerprint", "DeviceSoftware", "DeviceApplications", "DeviceOperatingSystem", "IPAddress",
    "MACAddress", "DeviceIdentifier", "DigitalFingerprint", "Identifier", "Location", "BirthPlace",
    "Country", "GPSCoordinate", "PhysicalAddress", "City", "HouseNumber", "Locality", "PostalCode",
    "Region", "RoomNumber", "Street", "TravelHistory", "UserAgent"
])


def calculate_metrics_per_segment_sets(entities_per_policy_per_segment_predicted,
                                       entities_per_policy_per_segment_annotated):
    # Calculate precision and recall for each policy segment and overall policy
    metrics_per_policy = {}

    for policy in entities_per_policy_per_segment_predicted.keys():
        metrics_per_policy[policy] = {'segments': {}}

        policy_true_positives = 0
        policy_false_positives = 0
        policy_false_negatives = 0

        for segment in entities_per_policy_per_segment_predicted[policy].keys():
            predicted = entities_per_policy_per_segment_predicted[policy][segment]
            annotated = entities_per_policy_per_segment_annotated[policy][segment]

            if len(predicted) == 0 and len(annotated) == 0:
                precision = 1.0
                recall = 1.0
                true_positives = 0
                false_positives_list = []
                false_negatives_list = []
            else:
                true_positives = len(predicted.intersection(annotated))
                false_positives_list = list(predicted - annotated)
                false_negatives_list = list(annotated - predicted)

                precision = true_positives / (true_positives + len(false_positives_list)) if (true_positives + len(
                    false_positives_list)) > 0 else 0
                recall = true_positives / (true_positives + len(false_negatives_list)) if (true_positives + len(
                    false_negatives_list)) > 0 else 0

            metrics_per_policy[policy]['segments'][segment] = {
                'precision': precision,
                'recall': recall,
                'true_positives': true_positives,
                'false_positives': {
                    'count': len(false_positives_list),
                    'items': false_positives_list
                },
                'false_negatives': {
                    'count': len(false_negatives_list),
                    'items': false_negatives_list
                }
            }

            # Accumulate for policy-level metrics
            policy_true_positives += true_positives
            policy_false_positives += len(false_positives_list)
            policy_false_negatives += len(false_negatives_list)

        # Calculate policy-level precision and recall
        if policy_true_positives == 0 and policy_false_positives == 0 and policy_false_negatives == 0:
            policy_precision = 1.0
            policy_recall = 1.0
        else:
            policy_precision = policy_true_positives / (policy_true_positives + policy_false_positives) if (
                                                                                                                       policy_true_positives + policy_false_positives) > 0 else 0
            policy_recall = policy_true_positives / (policy_true_positives + policy_false_negatives) if (
                                                                                                                    policy_true_positives + policy_false_negatives) > 0 else 0

        metrics_per_policy[policy]['overall'] = {
            'precision': policy_precision,
            'recall': policy_recall,
            'true_positives': policy_true_positives,
            'false_positives': policy_false_positives,
            'false_negatives': policy_false_negatives
        }

        return metrics_per_policy


# data entities
def data_entities_per_policy_per_segment_predicted(raw_dir):
    # get sets of predicted data entities
    data_entities_raw = get_data_entities_for_policies(raw_dir)

    data_entities_per_policy_per_segment_predicted = {}
    for policy, data in data_entities_raw.items():
        data_entities_per_policy = {}
        for file_name, entities in data.items():
            data_entities_per_policy[file_name] = {item['text'] for item in entities}
        data_entities_per_policy_per_segment_predicted[policy] = data_entities_per_policy

    return data_entities_per_policy_per_segment_predicted


def data_entities_per_policy_per_segment_annotated(annotated_dir):
    # get sets of annotated data entities (ground truth)
    data_entities = {}

    for subdir in os.listdir(annotated_dir):
        subdir_path = os.path.join(annotated_dir, subdir)

        data_entities_per_policy_annotated = {}
        i = 0
        while True:
            file_path = os.path.join(subdir_path, f"{i}.ann")

            if not os.path.exists(file_path):
                break

            parsed_annotation = parse_brat_file(file_path)
            data_entities_per_segment = set()
            parsed_entities = parsed_annotation["entities"]
            for entity in parsed_entities.values():
                if entity[1] in data_set:
                    data_entities_per_segment.add(entity[4])
            data_entities_per_policy_annotated[f"{i}.txt"] = data_entities_per_segment

            i += 1
        data_entities[subdir] = data_entities_per_policy_annotated

    return data_entities


def data_categories_per_policy_per_segment_predicted(raw_dir):
    data_entities = data_entities_per_policy_per_segment_predicted(raw_dir)

    data_categories_per_policy_per_segment_predicted = {}
    for policy, data in data_entities.items():
        data_categories_per_policy = {}
        for file_name, entities in data.items():
            # TODO: separately handle the case when entities is empty
            # LLM call to map phrases to categories
            categories_per_segment_raw = get_data_categories_for_list(list(entities))
            # print(categories_per_segment_raw)
            data_categories_per_policy[file_name] = {item['category'] for item in categories_per_segment_raw}
        data_categories_per_policy_per_segment_predicted[policy] = data_categories_per_policy

    return data_categories_per_policy_per_segment_predicted

def data_categories_per_policy_per_segment_annotated(annotated_dir):
    # get sets of annotated data categories (ground truth)
    data_categories = {}

    for subdir in os.listdir(annotated_dir):
        subdir_path = os.path.join(annotated_dir, subdir)

        data_categories_per_policy_annotated = {}
        i = 0
        while True:
            file_path = os.path.join(subdir_path, f"{i}.ann")

            if not os.path.exists(file_path):
                break

            parsed_annotation = parse_brat_file(file_path)
            data_categories_per_segment = set()
            parsed_entities = parsed_annotation["entities"]
            for entity in parsed_entities.values():
                if entity[1] in data_set:
                    data_categories_per_segment.add(entity[1])
            data_categories_per_policy_annotated[f"{i}.txt"] = data_categories_per_segment

            i += 1
        data_categories[subdir] = data_categories_per_policy_annotated

    return data_categories

# data_entities_metrics_per_segment("../data/original", "../data/annotations/reconciled/phase1")
predicted = data_entities_per_policy_per_segment_predicted("../../data/other/original")
annotated = data_entities_per_policy_per_segment_annotated("../../data/annotations/reconciled/phase1")
results = calculate_metrics_per_segment_sets(predicted, annotated)
for policy, data in results.items():
    print(f"Policy: {policy}")
    print(f"  Overall Precision: {data['overall']['precision']:.2f}")
    print(f"  Overall Recall: {data['overall']['recall']:.2f}")
    print("  Segments:")
    for segment, metrics in data['segments'].items():
        print(f"    Segment: {segment}")
        print(f"      Precision: {metrics['precision']:.2f}")
        print(f"      Recall: {metrics['recall']:.2f}")
        print(f"      False Positives ({metrics['false_positives']['count']}):")
        for item in metrics['false_positives']['items']:
            print(f"        - {item}")
        print(f"      False Negatives ({metrics['false_negatives']['count']}):")
        for item in metrics['false_negatives']['items']:
            print(f"        - {item}")
    print()

# predicted = data_categories_per_policy_per_segment_predicted("../data/original")
# annotated = data_categories_per_policy_per_segment_annotated("../data/annotations/reconciled/phase1")
# results = calculate_metrics_per_segment_sets(predicted, annotated)
# for policy, data in results.items():
#     print(f"Policy: {policy}")
#     print(f"  Overall Precision: {data['overall']['precision']:.2f}")
#     print(f"  Overall Recall: {data['overall']['recall']:.2f}")
#     print("  Segments:")
#     for segment, metrics in data['segments'].items():
#         print(f"    Segment: {segment}")
#         print(f"      Precision: {metrics['precision']:.2f}")
#         print(f"      Recall: {metrics['recall']:.2f}")
#         print(f"      False Positives ({metrics['false_positives']['count']}):")
#         for item in metrics['false_positives']['items']:
#             print(f"        - {item}")
#         print(f"      False Negatives ({metrics['false_negatives']['count']}):")
#         for item in metrics['false_negatives']['items']:
#             print(f"        - {item}")
#     print()