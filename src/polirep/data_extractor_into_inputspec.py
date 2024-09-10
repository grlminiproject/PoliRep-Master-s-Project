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

json_schema = {
    "name": "input_specs",
    "schema": {
        "type": "object",
        "properties": {
            "input_specs": {
                "type": "array",
                "description": "List of tuples.",
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "User private data collected, used, processed, or stored by the application.",
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Purpose for which this data will be used (if specified).",
                        },
                        "third_party": {
                            "type": "string",
                            "description": "Third parties to which this data will be provided (if applicable).",
                        },
                        "third_party_purpose": {
                            "type": "string",
                            "description": "Purpose for providing data to third parties (if specified).",
                        },
                    },
                    "required": ["data", "purpose", "third_party", "third_party_purpose"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["input_specs"],
        "additionalProperties": False
    },
    "strict": True
}

def load_prompt(file_path):
    with open(file_path, 'r') as file:
        prompt = file.read()
    return prompt

def process_file(filename, file_content, client, prompt):

    user_prompt = "Please process this file: \n {file_content}".format(file_content=file_content)

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema,
            }
        )
        print(response.choices[0].message)
        return json.loads(response.choices[0].message.content)["input_specs"]
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None


def extract_inputspec(root_dir, client, prompt):
    result = {}

    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)

        if os.path.isdir(subdir_path):
            result[subdir] = []

            i = 0
            while True:
                file_path = os.path.join(subdir_path, f"{i}.txt")

                if not os.path.exists(file_path):
                    break

                with open(file_path, 'r') as file:
                    file_content = file.read()

                chatgpt_response = process_file(f"{i}.txt", file_content, client, prompt)
                result[subdir].append(chatgpt_response)

                i += 1

                if i == 10:
                    break  # TODO: remove break
        break  # TODO: remove break
    return result


if __name__ == "__main__":
    prompt_path = "../../documents/prompts/DToU-one-shot.txt"
    prompt = load_prompt(prompt_path)
    policy_dir = "../../data/annotations/will_be_deleted"
    directory_dict = extract_inputspec(policy_dir, client, prompt)

    for subdir, responses in directory_dict.items():
        print(f"Subdirectory: {subdir}")
        for i, response in enumerate(responses):
            print(f"  File {i}.txt analysis:")
            print(f"  {response}")
            print()
        print("=" * 50)
