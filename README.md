# Learn-AI-Engineering
Code, notebooks, and other material for FuturePath AI's training course on Generative AI

## Setup Instructions
You can follow along with [this](https://www.loom.com/share/6adad8817d9b4f8281084e32e335614a?sid=ae2a71bc-2a84-4f8a-83b3-260a9881a506) video to setup the dependencies on your local. 
### Manual Setup 
1. Virtual Environment Setup<br>
    - Setup a virtual environment on your local machine using `pyenv` or `miniconda`.Using miniconda or pyenv ensures that you can switch between multiple python version seamlessly.<br>

    - Ensure the version of the python matches the version required in [pyproject.toml](pyproject.toml).Recommended version is >3.9 and <3.12 . 
    - Follow the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) to install pyenv. 
    - Install specific Python version and create a virtualenv using below commands
```
pyenv install 3.11.0
pyenv virtualenv  3.11.0 learn_ai
pyenv shell learn_ai
```
2. Install Dependencies <br>
```
pip install poetry==1.6.1
poetry install --no-cache
```
3. To Run the Notebooks select the kernal `learn_ai` in jupyter-notebook. 

### Running with Colab 

Add tocolab to the domain open a Github notebook directly in Colab i.e. replacing https://github.com with https://githubtocolab.com. 


Manually install all dependencies by adding them to “pip install” at the start of the notebook — for instance:

```
!pip install tiktoken voyager
```

Continue with the notebook!

## Assignments 

1. Kaggle: [LLM Prompting](https://kaggle.com/t/59bd358ed6834f60b242554b545894ae)

2. Augment (RAG Eval): [Augment](/rag_eval/augment.md)

3. Retriever (RAG Eval): [Retriever](/rag_eval/retriever.md)
