# String Phenomenology Dataset and LLM Fine-tuning

## Project Overview

This repository is dedicated to creating a specialized dataset around the field of string phenomenology, focusing on significant papers that have shaped the domain. The primary goal is to leverage this curated dataset to fine-tune a Large Language Model (LLM), particularly a Llama model, enhancing its understanding and generation capabilities regarding string phenomenology.

## Repository Structure

This repository is structured to facilitate easy access to the various components of the dataset creation and model fine-tuning process. Below is an overview of the top-level structure:

```
Llama-FineTuning/
|
├── DatasetCreation.ipynb # Jupyter notebook for the creation of the string phenomenology dataset
|
├── Llama-FineTuning.ipynb # Jupyter notebook for fine-tuning the Llama model
|
├── Datasets/ # Directory containing the compiled datasets used for fine-tuning
|
├── Files/ # Directory containing the papers on which the training is based
|
├── aux/ # Auxiliary directory with utility functions used in notebooks
|
├── LICENSE # The license file for the project
|
└── README.md # The README file for the project, providing an overview and instructions
```

### Detailed Description of Components

- **DatasetCreation.ipynb**: This notebook contains all the code and documentation used to create the dataset from selected papers. It includes data extraction, preprocessing, and compilation steps.

- **Llama-FineTuning.ipynb**: This notebook will be used to fine-tune the Llama model. It will contain the training algorithms, evaluation methods, and fine-tuning procedures.

- **Datasets/**: A folder that includes the datasets prepared for the model training. It is the output from `DatasetCreation.ipynb`.

- **Files/**: This folder holds the original papers and supporting documents that form the basis of the dataset. These are the primary sources for data extraction.

- **aux/**: The auxiliary folder includes additional scripts and functions that support the main notebooks. This is to keep utility functions organized and separate from the main codebase.

- **LICENSE**: The project's license file outlines the permissions and limitations for the use of this repository's content.

- **README.md**: The README document provides an introduction and guide to the repository, including project goals, usage, and contribution guidelines.

Feel free to navigate through the directories to find the specific components you are interested in. Each folder and file is documented to assist you in understanding its purpose and usage.


## Dataset Creation

The dataset for fine-tuning the Llama model is constructed from a series of influential papers in the field of string phenomenology. Each paper was carefully segmented into chunks, which were then processed through OpenAI's ChatGPT 3.5 Turbo. This state-of-the-art language model was utilized to generate technical-level questions based on the content of each paper segment, ensuring a rich, contextually relevant dataset aimed at enhancing the Llama model's capabilities in the domain of string phenomenology.


## Papers Included in the Dataset

The dataset has been created from the following papers:

- ['Physics of String Flux Compactifications' by F. Denef, M. R. Douglas, S. Kachru](https://inspirehep.net/literature/741903)
- ['String cosmology: From the early universe to today' by M. Cicoli, J. P. Conlon, A. Maharana, S. Parameswaran, F. Quevedo, I. Zavala](https://inspirehep.net/literature/2640110)
- ['Moduli Stabilization in String Theory' by L. McAllister, F. Quevedo](https://inspirehep.net/literature/2715847)
- ['Naturalness, String Landscape and Multiverse: A Modern Introduction with Exercises' by A. Hebecker](https://inspirehep.net/literature/1854305)
- ['The Swampland: Introduction and Review' by E. Palti](https://inspirehep.net/literature/1725205)

We plan to include many more papers in the field.

## Model Fine-tuning

Using the dataset, the fine-tuning process aims to integrate the detailed insights and complexities of string phenomenology into the Llama model. This will be achieved through advanced training techniques, ensuring the model accurately reflects the depth of knowledge contained in the papers.

## Features and Planned Implementations

### Current Features

- Dataset of key papers in string phenomenology
- Initial model training scripts

### Features to Add

- Enhanced data preprocessing for optimal model ingestion. For instance at the moment many questions refer to the text of the paper, which we want to avoid.
- Expanded dataset with additional papers and resources.
- Reatin the references (includng e.g. the arXiv number in the dataset, whenever that's necessary)
- Fine-tune a Llama model using the Dataset created.
- Implement a RAG system that is able to properly identify relevant papers in the field and discuss their findings.

## Collaboration and Feedback

We invite researchers, enthusiasts, and developers to contribute to this project. Your expertise and insights are invaluable to the success of this endeavor.

### How to Contribute

- **Adding to the Dataset**: If you have suggestions for papers or content that should be included, please open an issue or submit a pull request.
- **Model Training**: Contributions to the fine-tuning process or improvements to the training scripts are welcome.
- **Feature Suggestions**: Have ideas for new features or implementations? Let's discuss them in the issues section!

### Feedback

Please share your thoughts, constructive criticism, or reports of any issues you encounter.


## HuggingFace info

---
title: StringPheno
emoji: 👁
colorFrom: indigo
colorTo: indigo
sdk: streamlit
sdk_version: 1.31.1
app_file: app.py
pinned: false
license: apache-2.0
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
=======

