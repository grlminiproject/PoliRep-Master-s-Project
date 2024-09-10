
import os
from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt

from src.annotations_processing.brat_parser import parse_brat_file

ANNOTATIONS_DIR = "../../data/annotations/phases"
FINAL_BENCHMARK_DIR = "../../data/annotations/final_benchmark"

method_type_set = {"general-safeguard-method", "user-authentication", "encryptions", "Access-limitation", "Protection-other"}
operation_type_set = {"collection-use", "third-party-sharing-disclosure", "data-storage-retention-deletion",
                      "data-security-protection", "derivation"}

data_type_set = {"Data-general", "Data-aggregated-nonidentifiable", "Data-cookies-web-beacons-and-other-technologies",
                 "Data-user-online-activities-profiles", "Data-location", "Data-computer-device", "Data-finance",
                 "Data-contact", "Data-demographic", "Data-other", "Internal", "Authenticating", "Password", "PINCode",
                 "SecretText", "KnowledgeBelief", "PhilosophicalBelief", "ReligiousBelief", "Thought", "Preference",
                 "Favorite", "FavoriteColor", "FavoriteFood", "FavoriteMusic", "Intention", "Interest", "Dislike",
                 "Like", "Opinion", "PrivacyPreference", "External", "Behavioral", "Attitude", "AuthenticationHistory",
                 "BrowsingBehavior", "BrowserHistory", "BrowsingReferral", "CallLog", "Demeanor", "LinkClicked",
                 "Personality", "Reliability", "ServiceConsumptionBehavior", "TVViewingBehavior",
                 "AdInteractionBehavior", "Citizenship", "Demographic", "Geographic", "IncomeBracket", "PhysicalTrait",
                 "Ethnicity", "EthnicOrigin", "Race", "Identifying", "Biometric", "FacialPrint", "Fingerprint",
                 "Retina", "Name", "OfficialID", "Passport", "Picture", "UID", "Username", "VehicleLicense",
                 "VehicleLicenseNumber", "VehicleLicenseRegistration", "Language", "Accent", "Dialect", "MedicalHealth",
                 "BloodType", "Disability", "DNACode", "DrugTestResult", "Health", "Genetic", "MentalHealth",
                 "PhysicalHealth", "HealthHistory", "FamilyHealthHistory", "IndividualHealthHistory", "HealthRecord",
                 "Prescription", "Nationality", "PersonalDocuments", "PhysicalCharacteristic", "Age", "AgeRange",
                 "AgeExact", "BirthDate", "Gender", "HairColor", "Height", "Piercing", "SkinTone", "Tattoo", "Weight",
                 "Sexual", "Fetish", "Proclivity", "SexualHistory", "SexualPreference", "Vehicle", "VehicleUsage",
                 "Financial", "FinancialAccount", "AccountIdentifier", "FinancialAccountNumber", "BankAccount",
                 "PaymentCard", "PaymentCardExpiry", "PaymentCardNumber", "CreditCardNumber", "FinancialStatus",
                 "Insurance", "Ownership", "CarOwned", "HouseOwned", "ApartmentOwned", "PersonalPossession",
                 "Transactional", "Credit", "CreditCapacity", "CreditRecord", "CreditStanding", "CreditWorthiness",
                 "CreditScore", "Income", "LoanRecord", "Purchase", "PurchasesAndSpendingHabit", "Sale", "Tax",
                 "Transaction", "Historical", "LifeHistory", "Social", "Communication", "EmailContent", "SocialMedia",
                 "PubliclyAvailableSocialMedia", "SocialMediaCommunication", "VoiceCommunicationRecording", "VoiceMail",
                 "Criminal", "CriminalCharge", "CriminalConviction", "CriminalOffense", "CriminalPardon", "Family",
                 "FamilyStructure", "Divorce", "Marriage", "Offspring", "Parent", "Sibling", "Relationship",
                 "Professional", "DisciplinaryAction", "Education", "EducationExperience", "EducationQualification",
                 "EmploymentHistory", "CurrentEmployment", "PastEmployment", "Job", "PerformanceAtWork",
                 "ProfessionalCertification", "ProfessionalEvaluation", "ProfessionalInterview", "Reference", "Salary",
                 "School", "WorkEnvironment", "WorkHistory", "PublicLife", "Character", "CommunicationsMetadata",
                 "GeneralReputation", "Interaction", "MaritalStatus", "PoliticalAffiliation", "PoliticalOpinion",
                 "Religion", "SocialStatus", "SocialNetwork", "Acquantaince", "Association", "Connection", "Friend",
                 "GroupMembership", "TradeUnionMembership", "Tracking", "Contact", "EmailAddress",
                 "EmailAddressPersonal", "EmailAddressWork", "TelephoneNumber", "DeviceBased", "BrowserFingerprint",
                 "DeviceSoftware", "DeviceApplications", "DeviceOperatingSystem", "IPAddress", "MACAddress",
                 "DeviceIdentifier", "DigitalFingerprint", "Identifier", "Location", "BirthPlace", "Country",
                 "GPSCoordinate", "PhysicalAddress", "City", "HouseNumber", "Locality", "PostalCode", "Region",
                 "RoomNumber", "Street", "TravelHistory", "UserAgent", "Data"}

# Purpose-related words set
purpose_set = {"Purpose", "AccountManagement", "CommercialPurpose", "CommercialResearch", "CommunicationManagement",
               "CommunicationForCustomerCare", "CustomerManagement", "CustomerCare", "CustomerClaimsManagement",
               "CustomerOrderManagement", "CustomerRelationshipManagement", "ImproveInternalCRMProcesses",
               "CustomerSolvencyMonitoring", "CreditChecking", "MaintainCreditCheckingDatabase",
               "MaintainCreditRatingDatabase", "EnforceSecurity", "EnforceAccessControl", "IdentityAuthentication",
               "MisusePreventionAndDetection", "FraudPreventionAndDetection", "CounterMoneyLaundering",
               "MaintainFraudDatabase", "Verification", "AgeVerification", "IdentityVerification",
               "EstablishContractualAgreement", "FulfilmentOfObligation", "FulfilmentOfContractualObligation",
               "LegalCompliance", "ProtectionOfIPR", "HumanResourceManagement", "PersonnelManagement",
               "PersonnelHiring", "PersonnelPayment", "Marketing", "Advertising", "PersonalisedAdvertising",
               "TargetedAdvertising", "DirectMarketing", "PublicRelations", "SocialMediaMarketing",
               "NonCommercialPurpose", "NonCommercialResearch", "OrganisationGovernance", "DisputeManagement",
               "MemberPartnerManagement", "OrganisationComplianceManagement", "OrganisationRiskManagement",
               "Personalisation", "ServicePersonalisation", "PersonalisedBenefits",
               "ProvidePersonalisedRecommendations", "ProvideEventRecommendations", "ProvideProductRecommendations",
               "UserInterfacePersonalisation", "PublicBenefit", "CombatClimateChange", "Counterterrorism",
               "DataAltruism", "ImproveHealthcare", "ImprovePublicServices", "ImproveTransportMobility",
               "ProtectionOfNationalSecurity", "ProtectionOfPublicSecurity", "ProvideOfficialStatistics",
               "PublicPolicyMaking", "RecordManagement", "ResearchAndDevelopment", "AcademicResearch",
               "ScientificResearch", "ServiceProvision", "PaymentManagement", "RepairImpairments",
               "RequestedServiceProvision", "DeliveryOfGoods", "SearchFunctionalities", "SellProducts",
               "SellDataToThirdParties", "SellInsightsFromData", "SellProductsToDataSubject", "ServiceOptimisation",
               "OptimisationForConsumer", "OptimiseUserInterface", "OptimisationForController",
               "ImproveExistingProductsAndServices", "IncreaseServiceRobustness", "InternalResourceOptimisation",
               "ServiceRegistration", "ServiceUsageAnalytics", "TechnicalServiceProvision", "VendorManagement",
               "VendorPayment", "VendorRecordsManagement", "VendorSelectionAssessment", "RightsFulfillment",
               "Purpose-general", "Purpose-other"}

def parse_files_per_phase():
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    total_len = 0

    for phase in os.listdir(ANNOTATIONS_DIR):
        phase_path = os.path.join(ANNOTATIONS_DIR, phase)
        if not os.path.isdir(phase_path):
            continue

        for annotator in os.listdir(phase_path):
            annotator_path = os.path.join(phase_path, annotator)
            if not os.path.isdir(annotator_path):
                continue

            entities = []
            relations = []
            events = []

            for policy in os.listdir(annotator_path):
                policy_path = os.path.join(annotator_path, policy)
                if not os.path.isdir(policy_path):
                    continue

                for file in os.listdir(policy_path):
                    if file.endswith('.ann'):
                        file_path = os.path.join(policy_path, file)
                        file_data = parse_brat_file(file_path)

                        total_len +=len(file_data['entities'])
                        total_len +=len(file_data['relations'])
                        total_len += len(file_data['events'])

                        entities.extend(file_data['entities'].items())
                        relations.extend(file_data['relations'].items())
                        events.extend(file_data['events'].items())

            result[phase][annotator] = {
                "entities": entities,
                "relations": relations,
                "events": events
            }

    print(f"Total_len: {total_len}")

    return dict(result)



def get_todo_entity_statistics():
    data = parse_files_per_phase()
    statistics = {}

    for phase, annotators in data.items():
        phase_stats = {}
        for annotator, annotation_data in annotators.items():
            entities = annotation_data['entities']
            total_entities = len(entities)
            todo_count = sum(1 for _, entity in entities if entity[1] == 'TODO')
            average_todo = todo_count / total_entities if total_entities > 0 else 0
            phase_stats[annotator] = {
                'total_entities': total_entities,
                'todo_entities': todo_count,
                'average_todo': average_todo
            }
        statistics[phase] = phase_stats

    return statistics

def get_todo_relation_statistics():
    data = parse_files_per_phase()
    statistics = {}

    for phase, annotators in data.items():
        phase_stats = {}
        for annotator, annotation_data in annotators.items():
            entities =  annotation_data['entities']
            relations = annotation_data['relations']
            events = annotation_data['events']
            phase_stats[annotator] = {
                'total_entities': len(entities),
                'total_relations': len(relations),
                'total_events': len(events),
            }
        statistics[phase] = phase_stats

    return statistics

def analyze_annotations(root_dir):
    entities = []
    relations = []
    events = []

    for policy in os.listdir(root_dir):
        policy_path = os.path.join(root_dir, policy)
        if not os.path.isdir(policy_path):
            continue

        for file in os.listdir(policy_path):
            if file.endswith('.ann'):
                file_path = os.path.join(policy_path, file)
                file_data = parse_brat_file(file_path)

                entities.extend(file_data['entities'].values())
                relations.extend(file_data['relations'].values())
                events.extend(file_data['events'].values())

    # Calculate entity statistics
    entity_stats = Counter()
    entity_stats['Overall'] = len(entities)
    for entity in entities:
        entity_type = entity[1]
        if entity_type in {"Third-party-entity", "Third-party-name"}:
            entity_stats['Third-party'] += 1
        elif entity_type in data_type_set:
            entity_stats['Data-type'] += 1
        elif entity_type in purpose_set:
            entity_stats['Purpose'] += 1
        elif entity_type in {"Condition", "Opt-in"}:
            entity_stats['Condition'] += 1
        elif entity_type == "Negation":
            entity_stats['Negation'] += 1
        elif entity_type in method_type_set:
            entity_stats['Method-type'] += 1
        elif entity_type in operation_type_set:
            entity_stats['Operation'] += 1

    # Calculate event and relation statistics
    event_relation_stats = Counter()
    event_relation_stats['Overall'] = len(events) + len(relations)
    for event in events:
        event_type = event[1]
        if event_type in {"collection-use", "third-party-sharing-disclosure",
                          "data-storage-retention-deletion", "data-security-protection", "derivation"}:
            event_relation_stats[event_type] += 1

    for relation in relations:
        if relation[1] == "SUBSUME":
            event_relation_stats['subsumption'] += 1

    return {
        'entity_stats': dict(entity_stats),
        'event_relation_stats': dict(event_relation_stats)
    }


def visualize_statistics(statistics):
    entity_stats = statistics['entity_stats']
    event_relation_stats = statistics['event_relation_stats']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor('white')

    light_brown = '#D2B48C'
    bar_width = 0.6

    # Entity Statistics
    entity_order = ['Data-type', 'Purpose', 'Operation', 'Condition', 'Method-type', 'Third-party']
    entity_counts = [entity_stats[k] for k in entity_order]

    bars1 = ax1.bar(entity_order, entity_counts, color=light_brown, width=bar_width)
    ax1.set_ylabel('Count')
    ax1.set_title('Entity Statistics', fontsize=14)
    ax1.set_xticklabels(entity_order, rotation=45)
    ax1.tick_params(axis='x', labelrotation=45)

    # Adjust label positions
    for label in ax1.get_xticklabels():
        label.set_ha('right')
        label.set_va('top')

    # Add count labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height}', ha='center', va='bottom')

    # Add overall count
    ax1.text(0.5, 0.95, f"Overall: {entity_stats['Overall']}",
             ha='center', va='center', transform=ax1.transAxes,
             fontsize=12, fontstyle='italic')

    # Event and Relation Statistics
    event_order = ['collection-use', 'third-party-sharing-disclosure',
                   'data-storage-retention-deletion', 'data-security-protection',
                   'derivation', 'subsumption']
    event_counts = [event_relation_stats[k] for k in event_order]

    bars2 = ax2.bar(event_order, event_counts, color=light_brown, width=bar_width)
    ax2.set_ylabel('Count')
    ax2.set_title('Event and Relation Statistics', fontsize=14)
    ax2.set_xticklabels(event_order, rotation=45)
    ax2.tick_params(axis='x', labelrotation=45)

    # Adjust label positions
    for label in ax2.get_xticklabels():
        label.set_ha('right')
        label.set_va('top')

    # Add count labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height}', ha='center', va='bottom')

    # Add overall count
    ax2.text(0.5, 0.95, f"Overall: {event_relation_stats['Overall']}",
             ha='center', va='center', transform=ax2.transAxes,
             fontsize=12, fontstyle='italic')

    plt.tight_layout()
    plt.savefig('annotation_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()


def analyze_label_frequencies(root_dir):
    data_type_counter = Counter()
    purpose_counter = Counter()

    for policy in os.listdir(root_dir):
        policy_path = os.path.join(root_dir, policy)
        if not os.path.isdir(policy_path):
            continue

        for file in os.listdir(policy_path):
            if file.endswith('.ann'):
                file_path = os.path.join(policy_path, file)
                file_data = parse_brat_file(file_path)

                for entity in file_data['entities'].values():
                    entity_type = entity[1]  # Assuming the entity type is at index 1

                    if entity_type in data_type_set:
                        data_type_counter[entity_type] += 1
                    elif entity_type in purpose_set:
                        purpose_counter[entity_type] += 1

    return data_type_counter, purpose_counter


def visualize_top_labels(data_type_counter, purpose_counter):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('white')

    light_brown = '#D2B48C'
    bar_width = 0.6

    # Data Types
    data_types = [item for item in data_type_counter.most_common()
                  if item[0] not in {'Data-general', 'Data-other'}][:8]
    data_labels, data_counts = zip(*data_types)

    bars1 = ax1.bar(data_labels, data_counts, color=light_brown, width=bar_width)
    ax1.set_ylabel('Frequency', fontsize=18)
    ax1.set_title('Top 8 Data Classes', fontsize=18)
    ax1.set_xticklabels(data_labels, rotation=45, ha='right', fontsize=18)
    ax1.tick_params(axis='y', labelsize=18)  # Set y-axis tick label font size
    ax1.set_ylim(0, 50)

    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height}', ha='center', va='bottom', fontsize=18)

    # Purposes
    purposes = [item for item in purpose_counter.most_common()
                if item[0] not in {'Purpose-general', 'Purpose-other'}][:8]
    purpose_labels, purpose_counts = zip(*purposes)

    bars2 = ax2.bar(purpose_labels, purpose_counts, color=light_brown, width=bar_width)
    ax2.set_ylabel('Frequency', fontsize=18)
    ax2.set_title('Top 8 Purpose Classes', fontsize=18)
    ax2.set_xticklabels(purpose_labels, rotation=45, ha='right', fontsize=18)
    ax2.tick_params(axis='y', labelsize=18)  # Set y-axis tick label font size
    ax2.set_ylim(0, 40)

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height}', ha='center', va='bottom', fontsize=18)

    plt.tight_layout()
    plt.savefig('label_frequency_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":

    todo_statistics = get_todo_relation_statistics()

    for phase, annotators in todo_statistics.items():
        print(f"Phase: {phase}")
        for annotator, stats in annotators.items():
            print(f"  Annotator: {annotator}")
            print(f"    Total entities: {stats['total_entities']}")
            print(f"    Total relations: {stats['total_relations']}")
            print(f"    Total events: {stats['total_events']}")
        print()
