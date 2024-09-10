import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
client = OpenAI(api_key=openai_api_key)
client_anthropic = Anthropic(api_key=anthropic_api_key)


data_response_schema = {
    "name": "categories",
    "schema": {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The exact phrase from the given list.",
                        },
                        "category": {
                            "type": "string",
                            "description": "Data category from the hierarchy that matches each phrase the closest and most precisely.",
                            "enum": ["Internal", "Authenticating", "Password", "PINCode",
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
    "Region", "RoomNumber", "Street", "TravelHistory", "UserAgent"]
                        },
                    },
                    "required": ["phrase", "category"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["categories"],
        "additionalProperties": False
    },
    "strict": True
}

data_tool = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phrase": {
                                "type": "string",
                                "description": "The exact phrase from the given list.",
                            },
                            "category": {
                                "type": "string",
                                "description": "Data category from the hierarchy that matches each phrase the closest and most precisely.",
                                "enum": ["Internal", "Authenticating", "Password", "PINCode",
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
        "Region", "RoomNumber", "Street", "TravelHistory", "UserAgent"]
                            },
                        },
                        "required": ["phrase", "category"]
                    }
                }
            },
            "required": ["categories"]
        }
    }
]

purpose_response_schema = {
    "name": "categories",
    "schema": {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The exact phrase from the given list.",
                        },
                        "category": {
                            "type": "string",
                            "description": "Purpose category from the hierarchy that matches each phrase the closest and most precisely.",
                            "enum": ["AccountManagement", "CommercialPurpose", "CommercialResearch", "CommunicationManagement",
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
                                    "VendorPayment", "VendorRecordsManagement", "VendorSelectionAssessment", "RightsFulfillment"
                                    ]
                        },
                    },
                    "required": ["phrase", "category"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["categories"],
        "additionalProperties": False
    },
    "strict": True
}

purpose_tool = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phrase": {
                                "type": "string",
                                "description": "The exact phrase from the given list.",
                            },
                            "category": {
                                "type": "string",
                                "description": "Purpose category from the hierarchy that matches each phrase the closest and most precisely.",
                                "enum": ["AccountManagement", "CommercialPurpose", "CommercialResearch", "CommunicationManagement",
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
                                        "VendorPayment", "VendorRecordsManagement", "VendorSelectionAssessment", "RightsFulfillment"
                                        ]
                            },
                        },
                        "required": ["phrase", "category"]
                    }
                }
            },
            "required": ["categories"]
        }
    }
]

protection_method_response_schema = {
    "name": "categories",
    "schema": {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The exact phrase from the given list.",
                        },
                        "category": {
                            "type": "string",
                            "description": "Protection method from the list that matches each phrase the closest and most precisely.",
                            "enum": ["general-safeguard-method", "User-authentication", "encryptions", "Access-limitation", "Protection-other"]
                        },
                    },
                    "required": ["phrase", "category"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["categories"],
        "additionalProperties": False
    },
    "strict": True
}

protection_method_tool = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phrase": {
                                "type": "string",
                                "description": "The exact phrase from the given list.",
                            },
                            "category": {
                                "type": "string",
                                "description": "Protection method from the list that matches each phrase the closest and most precisely.",
                                "enum": ["general-safeguard-method", "User-authentication", "encryptions", "Access-limitation", "Protection-other"]
                            },
                        },
                        "required": ["phrase", "category"]
                    }
                }
            },
            "required": ["categories"]
        }
    }
]


def read_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read()


def create_prompt(hierarchy_file, definitions_file, base_prompt) -> str:
    hierarchy = read_file(hierarchy_file)
    definitions = read_file(definitions_file)
    prompt = base_prompt.format(hierarchy=hierarchy, definitions=definitions)
    return prompt


def parse_categories(categories):
    try:
        data = json.loads(categories)
        entity_list = data.get('categories', [])
        return entity_list
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return []
    except KeyError:
        print("Error: 'categories' key not found in the JSON data")
        return []


def get_categories_for_list(hierarchy_file, definitions_file, base_prompt, phrases, response_schema, model):
    system_prompt = create_prompt(hierarchy_file, definitions_file, base_prompt)
    user_prompt = "Please process this list of phrases: \n {phrases}".format(phrases="\n".join(phrases))

    if model == "OpenAI":
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": response_schema,
                }
            )
            # print(response.choices[0].message.content)
            return parse_categories(response.choices[0].message.content)
        except Exception as e:
            print(f"Error mapping phrases to categories: {str(e)}")
            return None
    elif model == "Anthropic":
        anthropic_prompt = base_prompt + "\n" + user_prompt + "\nUse the construction tool."
        response = client_anthropic.messages.create(
            model='claude-3-5-sonnet-20240620',
            max_tokens=4096,
            tools=response_schema,
            messages=[{"role": "user", "content": anthropic_prompt}]
        )
        json_entities = None
        for content in response.content:
            if content.type == "tool_use" and content.name == "construction":
                json_entities = content.input
                break

        if not json_entities:
            return json.loads('{}')

        return json_entities.get('categories', [])
    else:
        raise Exception(f"Model {model} not supported")

def get_data_categories_for_list(data, model):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hierarchy_file = os.path.join(current_dir, "../../documents/dvp", "data_hierarchy.txt")
    definitions_file = os.path.join(current_dir, "../../documents/dvp", "data_definitions.csv")
    base_prompt = os.path.join(current_dir, "../../documents/prompts", "data-mapping-struct.txt")
    response_schema = data_response_schema if model == "OpenAI" else data_tool
    return get_categories_for_list(hierarchy_file, definitions_file, base_prompt, data, response_schema, model)

def get_purpose_categories_for_list(purposes, model):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hierarchy_file = os.path.join(current_dir, "../../documents/dvp", "purpose_hierarchy.txt")
    definitions_file = os.path.join(current_dir, "../../documents/dvp", "purpose_definitions.csv")
    base_prompt = os.path.join(current_dir, "../../documents/prompts", "purpose-mapping-struct.txt")
    response_schema = purpose_response_schema if model == "OpenAI" else purpose_tool
    return get_categories_for_list(hierarchy_file, definitions_file, base_prompt, purposes, response_schema, model)

def get_protection_method_categories_for_list(methods, model):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_prompt = os.path.join(current_dir, "../../documents/prompts", "protection-method-struct.txt")
    user_prompt = "Please process this list of phrases: \n {phrases}".format(phrases="\n".join(methods))

    if model == "OpenAI":
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": protection_method_response_schema,
                }
            )
            # print(response.choices[0].message.content)
            return parse_categories(response.choices[0].message.content)
        except Exception as e:
            print(f"Error mapping phrases to categories: {str(e)}")
            return None
    elif model == "Anthropic":
        anthropic_prompt = base_prompt + "\n" + user_prompt + "\nUse the construction tool."
        response = client_anthropic.messages.create(
            model='claude-3-5-sonnet-20240620',
            max_tokens=4096,
            tools=protection_method_tool,
            messages=[{"role": "user", "content": anthropic_prompt}]
        )
        json_entities = None
        for content in response.content:
            if content.type == "tool_use" and content.name == "construction":
                json_entities = content.input
                break

        if not json_entities:
            return json.loads('{}')

        return json_entities.get('categories', [])
    else:
        raise Exception(f"Model {model} not supported")

