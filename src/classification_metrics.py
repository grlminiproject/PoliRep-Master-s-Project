import argparse
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.annotations_processing.brat_parser import get_polirep_per_policy_from_annotation, parse_brat_file
from src.polirep.categories_mapper_struct import get_data_categories_for_list, get_purpose_categories_for_list, \
    get_protection_method_categories_for_list

data_type_set = {"Internal", "Authenticating", "Password", "PINCode",
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
                 "RoomNumber", "Street", "TravelHistory", "UserAgent"}

# Purpose-related words set
purpose_set = {"AccountManagement", "CommercialPurpose", "CommercialResearch", "CommunicationManagement",
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
               "VendorPayment", "VendorRecordsManagement", "VendorSelectionAssessment", "RightsFulfillment"}

protection_method_set = {"general-safeguard-method", "User-authentication", "encryptions", "Access-limitation", "Protection-other"}


def calculate_metrics(all_policies_predicted, all_policies_annotated):
    categories = ['data', 'purpose', 'protection_method']
    results = {}

    for category in categories:
        predicted = set()
        annotated = set()

        for policy in all_policies_predicted:
            predicted.update(policy[category + '_predicted_set'])
        for policy in all_policies_annotated:
            annotated.update(policy[category + '_annotated_set'])

        true_positives = len(predicted.intersection(annotated))
        false_positives = len(predicted - annotated)
        false_negatives = len(annotated - predicted)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        # Calculate F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        results[category] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }

    return results


# Example usage:
def metrics(policies_dir, model):
    all_policies_predicted = []
    all_policies_annotated = []

    for policy_folder in os.listdir(policies_dir):
        policy_path = os.path.join(policies_dir, policy_folder)
        if os.path.isdir(policy_path):
            policy_predicted = {'data_predicted_set': set(), 'purpose_predicted_set': set(),
                                'protection_method_predicted_set': set()}
            policy_annotated = {'data_annotated_set': set(), 'purpose_annotated_set': set(),
                                'protection_method_annotated_set': set()}

            i = 0
            while True:
                file_path = os.path.join(policy_path, f"{i}.ann")
                if not os.path.exists(file_path):
                    break

                annotation = parse_brat_file(file_path)

                data_list = []
                data_annotated_set = set()

                purpose_list = []
                purpose_annotated_set = set()

                protection_method_list = []
                protection_method_annotated_set = set()

                for entity_id, entity in annotation["entities"].items():
                    if entity[1] in data_type_set:
                        data_list.append(entity[4])
                        data_annotated_set.add((entity[4], entity[1]))
                    elif entity[1] in purpose_set:
                        purpose_list.append(entity[4])
                        purpose_annotated_set.add((entity[4], entity[1]))
                    elif entity[1] in protection_method_set:
                        protection_method_list.append(entity[4])
                        protection_method_annotated_set.add((entity[4], entity[1]))

                # print("data_list: " + str(data_list))
                data_predicted_set = set()
                if data_annotated_set:
                    data_predicted_list = get_data_categories_for_list(data_list, model)
                    for el in data_predicted_list:
                        data_predicted_set.add((el["phrase"], el["category"]))

                purpose_predicted_set = set()
                if purpose_annotated_set:
                    purpose_predicted_list = get_purpose_categories_for_list(purpose_list, model)
                    for el in purpose_predicted_list:
                        purpose_predicted_set.add((el["phrase"], el["category"]))

                protection_method_predicted_set = set()
                if protection_method_annotated_set:
                    protection_method_predicted_list = get_protection_method_categories_for_list(protection_method_list,
                                                                                                 model)
                    for el in protection_method_predicted_list:
                        protection_method_predicted_set.add((el["phrase"], el["category"]))

                # Update the sets for this policy
                policy_predicted['data_predicted_set'].update(data_predicted_set)
                policy_predicted['purpose_predicted_set'].update(purpose_predicted_set)
                policy_predicted['protection_method_predicted_set'].update(protection_method_predicted_set)

                policy_annotated['data_annotated_set'].update(data_annotated_set)
                policy_annotated['purpose_annotated_set'].update(purpose_annotated_set)
                policy_annotated['protection_method_annotated_set'].update(protection_method_annotated_set)


                i += 1

            all_policies_predicted.append(policy_predicted)
            all_policies_annotated.append(policy_annotated)

    # Calculate metrics across all policies
    metrics_results = calculate_metrics(all_policies_predicted, all_policies_annotated)

    print("Metrics across all policies:")
    for category, metrics in metrics_results.items():
        print(f"{category.capitalize()}:")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall: {metrics['recall']:.4f}")
        print(f"  F1 Score: {metrics['f1_score']:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute classification metrics for policies.")
    parser.add_argument("policies_dir", help="Path to the directory containing policy folders")
    parser.add_argument("model", choices=["OpenAI", "Anthropic"], help="Model to use (OpenAI or Anthropic)")
    args = parser.parse_args()

    metrics(args.policies_dir, args.model)

