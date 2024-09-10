import json
import os
from collections import defaultdict

from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
client = OpenAI(api_key=openai_api_key)
client_anthropic = Anthropic(api_key=anthropic_api_key)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_ENTITIES_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "entities", "data_entities.txt"))
PURPOSE_ENTITIES_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "entities", "purpose_entities.txt"))
THIRD_PARTY_ENTITIES_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "entities", "third_party_entities.txt"))
PROTECTION_METHOD_ENTITIES_PROMPT_FILE = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "..", "documents", "prompts", "entities", "protection_method_entities.txt"))

data_schema = {
    "name": "data_entities",
    "schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of the context in which this datum is mentioned.",
                        },
                        "text": {
                            "type": "string",
                            "description": "The exact text of the data entity as it appears in the text segment.",
                        },
                    },
                    "required": ["type", "text"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["entities"],
        "additionalProperties": False
    },
    "strict": True
}

data_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The type of the context in which this datum is mentioned.",
                            },
                            "text": {
                                "type": "string",
                                "description": "The exact text of the data entity as it appears in the text segment.",
                            },
                        },
                        "required": ["type", "text"]
                    }
                }
            },
            "required": ["entities"]
        }
    }
]

purpose_schema = {
    "name": "purpose_entities",
    "schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of the context in which this purpose is mentioned.",
                        },
                        "text": {
                            "type": "string",
                            "description": "The exact text of the purpose entity as it appears in the text segment.",
                        },
                    },
                    "required": ["type", "text"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["entities"],
        "additionalProperties": False
    },
    "strict": True
}

purpose_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The type of the context in which this purpose is mentioned.",
                            },
                            "text": {
                                "type": "string",
                                "description": "The exact text of the purpose entity as it appears in the text segment.",
                            },
                        },
                        "required": ["type", "text"]
                    }
                }
            },
            "required": ["entities"]
        }
    }
]

third_party_schema = {
    "name": "third_party_entities",
    "schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The type of the context in which this third party entity is mentioned.",
                        },
                        "text": {
                            "type": "string",
                            "description": "The exact text of the third party entity as it appears in the text segment.",
                        },
                    },
                    "required": ["type", "text"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["entities"],
        "additionalProperties": False
    },
    "strict": True
}

third_party_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "List of tuples.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The type of the context in which this third party entity is mentioned.",
                            },
                            "text": {
                                "type": "string",
                                "description": "The exact text of the third party entity as it appears in the text segment.",
                            },
                        },
                        "required": ["type", "text"]
                    }
                }
            },
            "required": ["entities"]
        }
    }
]

protection_method_schema = {
    "name": "data_entities",
    "schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "description": "List of strings.",
                "items": {
                    "type": "string",
                    "description": "The exact text of the protection method entity as it appears in the text segment.",
                }
            }
        },
        "required": ["entities"],
        "additionalProperties": False
    },
    "strict": True
}

protection_method_tools = [
    {
        "name": "construction",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "List of strings.",
                    "items": {
                        "type": "string",
                        "description": "The exact text of the protection method entity as it appears in the text segment.",
                    }
                }
            },
            "required": ["entities"]
        }
    }
]

def read_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read()

def get_entity_type_per_segment(system_prompt_file_path, json_schema, segment_file_path, model):
    system_prompt = read_file(system_prompt_file_path)
    segment_content = read_file(segment_file_path)
    user_prompt = "Please process this policy segment: \n {file_content}".format(file_content=segment_content)

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
            return parse_entities(response.choices[0].message.content)
        except Exception as e:
            print(f"Error processing {segment_file_path}: {str(e)}")
            return None
    elif model == "Anthropic":
        anthropic_prompt = system_prompt+"\n"+user_prompt+f"\nUse the construction tool."
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

        if not json_entities:
            return json.loads('{}')

        return json_entities.get('entities', [])

    else:
        raise Exception(f"Model {model} not supported")


def get_raw_entities_per_segment(segment_file_path, model):
    data_json_schema = data_schema if model == "OpenAI" else data_tools
    purpose_json_schema = purpose_schema if model == "OpenAI" else purpose_tools
    third_party_json_schema = third_party_schema if model == "OpenAI" else third_party_tools
    protection_method_json_schema = protection_method_schema if model == "OpenAI" else protection_method_tools

    data_entities = get_entity_type_per_segment(DATA_ENTITIES_PROMPT_FILE, data_json_schema, segment_file_path, model)
    print(data_entities)
    purpose_entities = get_entity_type_per_segment(PURPOSE_ENTITIES_PROMPT_FILE, purpose_json_schema, segment_file_path, model)
    third_party_entities = get_entity_type_per_segment(THIRD_PARTY_ENTITIES_PROMPT_FILE, third_party_json_schema, segment_file_path, model)
    protection_method_entities = get_entity_type_per_segment(PROTECTION_METHOD_ENTITIES_PROMPT_FILE, protection_method_json_schema, segment_file_path, model)

    entities_raw = defaultdict(list)

    def add_unique(key, item):
        if item not in entities_raw[key]:
            entities_raw[key].append(item)

    for data_entity in data_entities:
        add_unique("data", (data_entity["text"], data_entity["type"]))

    for purpose_entity in purpose_entities:
        add_unique("purpose", (purpose_entity["text"], purpose_entity["type"]))

    for third_party_entity in third_party_entities:
        add_unique("third-party", (third_party_entity["text"], third_party_entity["type"]))

    for text in protection_method_entities:
        add_unique("protection-method", text)

    return entities_raw

def get_entities_per_segment2(system_prompt, user_prompt, json_schema, filename):
    # #ANTHROPIC
    # anthropic_prompt = system_prompt+"\n"+user_prompt+"\nUse the data_entities tool."
    # response = client_anthropic.messages.create(
    #     model='claude-3-5-sonnet-20240620',
    #     max_tokens=4096,
    #     tools=tools,
    #     messages=[{"role": "user", "content": anthropic_prompt}]
    # )
    # json_entities = None
    # for content in response.content:
    #     if content.type == "tool_use" and content.name == "data_entities":
    #         json_entities = content.input
    #         break
    #
    # return json_entities.get('entities', [])

    # if json_entities:
    #     print("Extracted Entities (JSON):")
    #     print(json_entities)
    # else:
    #     print("No entities found in the response.")

    #OPENAI
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
        return parse_entities(response.choices[0].message.content)
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None

def parse_entities(entities):
    try:
        # Parse the JSON string
        data = json.loads(entities)

        # Extract the list of entities
        entity_list = data.get('entities', [])

        # Return the list of entity dictionaries
        return entity_list
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return []
    except KeyError:
        print("Error: 'entities' key not found in the JSON data")
        return []


def get_entities_for_policies(base_dir, entities_prompt_file, json_schema):
    results = {}

    # Iterate through folders in the base directory
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            folder_results = {}

            txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

            i = 0  # TODO: remove
            for file_name in txt_files:
                i += 1
                if i < 4:
                    continue
                # TODO: remove

                entities_prompt = read_file(entities_prompt_file)

                file_path = os.path.join(folder_path, file_name)
                segment_content = read_file(file_path)
                user_prompt = "Please process this policy segment: \n {file_content}".format(file_content=segment_content)

                entities = get_entities_per_segment2(entities_prompt, user_prompt, json_schema, file_name)

                folder_results[file_name] = entities

                if i == 6:  # TODO: remove
                    break

            results[folder] = folder_results
        break  # TODO: remove
    return results




def get_data_entities_for_policies(raw_dir):
    entities_prompt_file = "../../../documents/prompts/entities/data_entities.txt"
    return get_entities_for_policies(raw_dir, entities_prompt_file, data_schema)


if __name__ == "__main__":

    segment_file_path = "../../../data/annotations/final_benchmark/air_com_qublix_solitaireblitz/3.ann"
    purpose_entities = get_entity_type_per_segment(PURPOSE_ENTITIES_PROMPT_FILE, purpose_schema, segment_file_path, "OpenAI")
    print(purpose_entities)


    segment_file_path = "../../../data/annotations/final_benchmark/air_com_qublix_solitaireblitz/3.ann"
    purpose_entities = get_entity_type_per_segment(PURPOSE_ENTITIES_PROMPT_FILE, purpose_schema, segment_file_path,
                                                   "OpenAI")
    print(purpose_entities)
