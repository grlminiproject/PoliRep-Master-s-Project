import json
import os
from collections import defaultdict

from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

from src.polirep.annotators.entities_annotator import get_raw_entities_per_segment

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
client = OpenAI(api_key=openai_api_key)
client_anthropic = Anthropic(api_key=anthropic_api_key)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PURPOSE_RELATION_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "relations", "purpose_relations.txt"))
DISCLOSURE_RELATION_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "relations", "disclosure_relations.txt"))
PROTECTION_RELATION_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "relations", "protection_relations.txt"))

purpose_relation_schema = {
    "name": "purpose_relations",
    "schema": {
        "type": "object",
        "properties": {
            "relations": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "The ID of data entity.",
                        },
                        "target": {
                            "type": "string",
                            "description": "The ID of purpose entity.",
                        },
                    },
                    "required": ["source", "target"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["relations"],
        "additionalProperties": False
    },
    "strict": True
}

purpose_relation_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "relations": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "The ID of data entity.",
                            },
                            "target": {
                                "type": "string",
                                "description": "The ID of purpose entity.",
                            },
                        },
                        "required": ["source", "target"]
                    }
                }
            },
            "required": ["relations"]
        }
    }
]

disclosure_relation_schema = {
    "name": "disclosure_relations",
    "schema": {
        "type": "object",
        "properties": {
            "relations": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "The ID of data entity.",
                        },
                        "target": {
                            "type": "string",
                            "description": "The ID of third party entity.",
                        },
                    },
                    "required": ["source", "target"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["relations"],
        "additionalProperties": False
    },
    "strict": True
}

disclosure_relation_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "relations": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "The ID of data entity.",
                            },
                            "target": {
                                "type": "string",
                                "description": "The ID of purpose entity.",
                            },
                        },
                        "required": ["source", "target"]
                    }
                }
            },
            "required": ["relations"]
        }
    }
]

protection_relation_schema = {
    "name": "protection_relations",
    "schema": {
        "type": "object",
        "properties": {
            "relations": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "The ID of data entity.",
                        },
                        "target": {
                            "type": "string",
                            "description": "The ID of protection method entity.",
                        },
                    },
                    "required": ["source", "target"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["relations"],
        "additionalProperties": False
    },
    "strict": True
}

protection_relation_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "relations": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "The ID of data entity.",
                            },
                            "target": {
                                "type": "string",
                                "description": "The ID of purpose entity.",
                            },
                        },
                        "required": ["source", "target"]
                    }
                }
            },
            "required": ["relations"]
        }
    }
]

def read_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read()

def get_relation_type_per_segment(system_prompt_file_path, segment_file_path, source_entity_json, target_entity_json, json_schema, model):
    system_prompt = read_file(system_prompt_file_path)
    segment_text = read_file(segment_file_path)
    # user_prompt = ("Please process this policy segment: \n{segment_text}\nData entities:\n{source_entities}\nPurpose_entities\n{"
    #  "target_entities}").format(segment_text=segment_text, source_entities=source_entity_json,
    #                             target_entities=target_entity_json)
    user_prompt = ("Please process this policy segment: \n{segment_text}\n{source_entities}\n{target_entities}"
                   .format(segment_text=segment_text, source_entities=source_entity_json,
                           target_entities=target_entity_json))
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
                    "json_schema": json_schema,
                }
            )
            # print(response.choices[0].message.content)
            return json.loads(response.choices[0].message.content)["relations"]
        except Exception as e:
            print(f"Error processing {segment_file_path}: {str(e)}")
            return None
    elif model == "Anthropic":
        anthropic_prompt = system_prompt + "\n" + user_prompt + "\nUse the construction tool."
        response = client_anthropic.messages.create(
            model='claude-3-5-sonnet-20240620',
            max_tokens=4096,
            tools=json_schema,
            messages=[{"role": "user", "content": anthropic_prompt}]
        )
        json_entities = None
        for content in response.content:
            if content.type == "tool_use" and content.name == "construction":
                json_entities = content.input
                break

        # print(response)

        if not json_entities:
            return json.loads('{}')

        # print(json_entities.get('entities', []))
        return json_entities.get('relations', [])
    else:
        raise Exception(f"Model {model} not supported")


def id_generator(prefix):
    counter = 1
    while True:
        yield f"{prefix}{counter}"
        counter += 1

def get_relations_per_segment(segment_file_path, model):
    entities_raw = get_raw_entities_per_segment(segment_file_path, model)

    # Assign entities IDs
    entities_raw_with_ids = defaultdict(list)
    data_id = id_generator("D")
    purpose_id = id_generator("P")
    third_party_id = id_generator("T")
    protection_method_id = id_generator("M")

    for category, entries in entities_raw.items():
        if category == "data":
            for text, operation in entries:
                entities_raw_with_ids[category].append((next(data_id), text, operation))
        elif category == "purpose":
            for text, operation in entries:
                entities_raw_with_ids[category].append((next(purpose_id), text, operation))
        elif category == "third-party":
            for text, operation in entries:
                entities_raw_with_ids[category].append((next(third_party_id), text, operation))
        elif category == "protection-method":
            for text in entries:
                entities_raw_with_ids[category].append((next(protection_method_id), text))

    relations_raw = defaultdict(set)

    # Purpose relations
    data_for_purpose_relation = []
    for data in entities_raw_with_ids["data"]:
        if data[2] in ["first-party-collection-use", "third-party-collection-use", "third-party-sharing-disclosure", "data-storage-retention-deletion"]:
            data_for_purpose_relation.append((data[0], data[1]))

    if len(data_for_purpose_relation) != 0 and len(entities_raw_with_ids["purpose"]) != 0:
        data_entities_for_purpose_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in data_for_purpose_relation
            ]
        }
        data_entities_for_purpose_relation_json_part = json.dumps(data_entities_for_purpose_relation, indent=2)
        data_for_purpose_relation_json = f"Data entities:\n{data_entities_for_purpose_relation_json_part}"

        purpose_entities_for_purpose_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in entities_raw_with_ids["purpose"]
            ]
        }

        purpose_entities_for_purpose_relation_json_part = json.dumps(purpose_entities_for_purpose_relation, indent=2)
        purpose_for_purpose_relation_json = f"Purpose entities:\n{purpose_entities_for_purpose_relation_json_part}"
        purpose_relation_json_schema = purpose_relation_schema if model == "OpenAI" else purpose_relation_tools
        purpose_relations = get_relation_type_per_segment(PURPOSE_RELATION_PROMPT_FILE,
                                                          segment_file_path,
                                                          data_for_purpose_relation_json,
                                                          purpose_for_purpose_relation_json,
                                                          purpose_relation_json_schema,
                                                          model)
        if purpose_relations:
            purpose_tuples = set([(relation["source"], relation["target"]) for relation in purpose_relations])
            relations_raw["purpose"] = purpose_tuples
            # print(purpose_tuples)

    # Disclosure relations
    data_for_disclosure_relation = []
    for data in entities_raw_with_ids["data"]:
        if data[2] == "third-party-sharing-disclosure":
            data_for_disclosure_relation.append((data[0], data[1]))

    if len(data_for_disclosure_relation) != 0 and len(entities_raw_with_ids["third-party"]) != 0:
        data_entities_for_disclosure_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in data_for_disclosure_relation
            ]
        }
        data_entities_for_disclosure_relation_json_part = json.dumps(data_entities_for_disclosure_relation, indent=2)
        data_for_disclosure_relation_json = f"Data entities:\n{data_entities_for_disclosure_relation_json_part}"

        third_parties_for_disclosure_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in entities_raw_with_ids["third-party"]
            ]
        }
        third_parties_for_disclosure_relation_json_part = json.dumps(third_parties_for_disclosure_relation, indent=2)
        third_parties_for_disclosure_relation_json = f"Third party entities:\n{third_parties_for_disclosure_relation_json_part}"
        disclosure_relation_json_schema = disclosure_relation_schema if model == "OpenAI" else disclosure_relation_tools
        disclosure_relations = get_relation_type_per_segment(DISCLOSURE_RELATION_PROMPT_FILE,
                                                          segment_file_path,
                                                          data_for_disclosure_relation_json,
                                                          third_parties_for_disclosure_relation_json,
                                                          disclosure_relation_json_schema,
                                                          model)
        if disclosure_relations:
            disclosure_tuples = set([(relation["source"], relation["target"]) for relation in disclosure_relations])
            relations_raw["disclosure"] = disclosure_tuples
            # print(disclosure_tuples)

    # Protection relations
    data_for_protection_relation = []
    for data in entities_raw_with_ids["data"]:
        if data[2] == "data-security-protection":
            data_for_protection_relation.append((data[0], data[1]))

    if len(data_for_protection_relation) != 0 and len(entities_raw_with_ids["protection-method"]) != 0:

        data_entities_for_protection_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in data_for_protection_relation
            ]
        }
        data_entities_for_protection_relation_json_part = json.dumps(data_entities_for_protection_relation, indent=2)
        data_for_protection_relation_json = f"Data entities:\n{data_entities_for_protection_relation_json_part}"

        methods_for_protection_relation = {
            "entities": [
                {"id": item[0], "text": item[1]} for item in entities_raw_with_ids["protection-method"]
            ]
        }
        methods_for_protection_relation_json_part = json.dumps(methods_for_protection_relation, indent=2)
        methods_for_protection_relation_json = f"Protection method entities:\n{methods_for_protection_relation_json_part}"
        protection_relation_json_schema = protection_relation_schema if model == "OpenAI" else protection_relation_tools
        protection_relations = get_relation_type_per_segment(PROTECTION_RELATION_PROMPT_FILE,
                                                             segment_file_path,
                                                             data_for_protection_relation_json,
                                                             methods_for_protection_relation_json,
                                                             protection_relation_json_schema,
                                                             model)
        if protection_relations:
            protection_tuples = set([(relation["source"], relation["target"]) for relation in protection_relations])
            relations_raw["protection"] = protection_tuples
            print(protection_tuples)

    return entities_raw_with_ids, relations_raw

if __name__ == "__main__":
    segment_file_path = "../../../data/annotations/final_benchmark/air_com_qublix_solitaireblitz/3.ann"
    get_relations_per_segment(segment_file_path, "Anthropic")
