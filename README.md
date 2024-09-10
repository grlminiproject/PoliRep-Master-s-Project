# PoliRep: Automated Privacy Policy Analysis Framework

PoliRep is a novel framework for automated privacy policy analysis and formalization using large language models (LLMs). It maps privacy policies to sophisticated ontologies at a fine granularity level and generates structured representations.

## Features

- Entity extraction from privacy policy text
- Fine-grained entity classification using Data Privacy Vocabulary (DPV) taxonomies
- Semantic relation extraction between policy elements
- Conversion to formal policy languages (e.g. Data Terms of Use)
- Knowledge graph generation for policy visualization

## Dataset

We provide a custom annotated dataset based on the PolicyIE corpus, with fine-grained annotations aligned with the DPV ontology. The dataset is available in the `data/annotations/final_benchmark` directory. This dataset includes:

- 10 privacy policies with detailed annotations
- Fine-grained entity labels for Data, Purpose, and other categories
- Semantic relations between entities
- Annotations aligned with the Data Privacy Vocabulary (DPV)

Researchers can use this dataset to:
- Evaluate their own privacy policy analysis tools
- Train machine learning models for policy understanding
- Benchmark performance against PoliRep results

To use the dataset in your own projects, you can load the annotation files from the `data/annotations/final_benchmark` directory. For more information on the dataset structure and annotation scheme, please refer to the `dataset_README.md` file in the same directory.


## Requirements

This project requires several Python libraries to function properly. You can install all necessary dependencies using the `requirements.txt` file provided in the repository.

### Dependencies

The main requirements for this project are:

- anthropic==0.34.2
- bratiaa==0.1.4
- matplotlib==3.9.2
- networkx==3.3
- openai==1.44.1
- python-dotenv==1.0.1

### Installation

To install the required packages, run the following command in your terminal:

```
pip install -r requirements.txt
```

Make sure you're in the project's root directory when running this command.

### Note

- It's recommended to use a virtual environment to avoid conflicts with other projects.
- Ensure you have Python 3.x installed on your system before installing the requirements.
- Some packages may require additional system-level dependencies. If you encounter any issues during installation, please refer to the individual package documentation for troubleshooting.

## API Key Setup

To use this project, you need to set up your OpenAI and Anthropic API keys:

1. Copy the `.env.example` file to a new file named `.env`:
   ```
   cp .env.example .env
   ```

2. Open the `.env` file and replace the placeholder text with your actual API keys. Do not use quotation marks around the keys:
   ```
   OPENAI_API_KEY=sk-1234567890abcdefghijklmnop
   ANTHROPIC_API_KEY=sk-ant-1234567890abcdefghijklmnop
   ```

3. Save the `.env` file. The project will now use your API keys when making requests to the respective APIs.

**Note:** 
- Never commit your `.env` file or share your API keys publicly. 
- The `.env` file is listed in `.gitignore` to prevent accidental commits.
- Do not use quotation marks around your API keys in the `.env` file.

## Running the Overall Performance Benchmark

To evaluate the overall performance of the model on policy analysis, you can use the `metrics.py` script. This script computes precision, recall, and F1 scores for entity and relation extraction tasks across multiple policies.

### Usage

Run the following command from the project root directory:

```
python src/metrics.py <path_to_policies_directory> <model_name>
```

### Parameters

- `<path_to_policies_directory>`: The path to the directory containing the annotated policy folders.
- `<model_name>`: The name of the model to evaluate. Use either "OpenAI" or "Anthropic".

### Example

```
python src/metrics.py data/annotations/fully_annotated_benchmark Anthropic
```

This command will run the performance benchmark on the policies in the `data/annotations/fully_annotated_benchmark` directory using the Anthropic model.

### Output

The script will print the precision, recall, and F1 scores for various entity types and relations extracted from the policies. The results are aggregated across all policies in the specified directory.

### Note

Make sure you have the necessary dependencies installed and that you're running the command from the project root directory (the directory containing the `src` folder).


## Processing and Visualising Your Privacy Policy

You can process your own privacy policy into the PoliRep (Policy Representation) specification and visualize it using the `visualize.py` script. This script extracts entities and relations from the policy text and generates a visual representation of the PoliRep.

### Usage

Run the following command from the project root directory:

```
python src/polirep/visualize.py <policy_path> <model_name>
```

### Parameters

- `<policy_path>`: The path to the folder containing the privacy policy you want to process and visualize. This folder should contain the policy text file.
- `<model_name>`: The name of the model to use for processing. Use either "OpenAI" or "Anthropic".

### Example

```
python src/polirep/visualize.py data/annotations/final_benchmark/9gag OpenAI
```

This command will process the privacy policy located in the `data/annotations/final_benchmark/9gag` folder using the OpenAI model, generate the PoliRep specification, and create a visualization of the extracted entities and relations.

### Output

The script will perform the following actions:
1. Process the privacy policy text into the PoliRep specification.
2. Generate a visual representation of the PoliRep, showing the entities and relations extracted from the policy.
3. Save the visualization results under the `src/polirep/output/` directory.


This tool allows you to quickly analyze and visualise the key components of any privacy policy, helping you understand its structure and content in the PoliRep format. The saved output in `src/polirep/output/` enables you to review and share the results easily.


## Computing Classification Metrics

You can compute classification metrics for a set of policies using the `classification_metrics.py` script. This script evaluates the performance of the model in classifying various aspects of privacy policies.

### Usage

Run the following command from the project root directory:

```
python src/classification_metrics.py <policies_dir> <model>
```

### Parameters

- `<policies_dir>`: The path to the directory containing the policy folders to be evaluated.
- `<model>`: The name of the model to use for evaluation. Use either "OpenAI" or "Anthropic".

### Example

```
python src/classification_metrics.py data/annotations/final_benchmark Anthropic
```

This command will compute classification metrics for the policies in the `data/annotations/final_benchmark` directory using the Anthropic model.

### Output

The script will calculate and display various classification metrics, which may include accuracy, precision, recall, and F1 score for different aspects of privacy policy classification.

### Note


- Computation time will vary depending on the number of policies.

This tool provides valuable insights into the model's performance in classifying different elements of privacy policies, helping you assess its effectiveness and identify areas for improvement.
