# Learn-AI-Engineering
Code, notebooks, and other material for FuturePath AI's training course on Generative AI

## Setup Instructions
You can follow along with [this](https://www.loom.com/share/6adad8817d9b4f8281084e32e335614a?sid=ae2a71bc-2a84-4f8a-83b3-260a9881a506) video to setup the dependencies on your local. 

### Manual Setup 
1. Clone the Repository and set your working directory
```bash
git clone https://github.com/FuturePathAI/Learn-AI-Engineering.git
cd Learn-AI-Engineering
```

2. Virtual Environment Setup
    - Setup a virtual environment on your local machine using `pyenv` or `miniconda`.Using miniconda or pyenv ensures that you can switch between multiple python version seamlessly.<br>
    - Ensure the version of the python matches the version required in [pyproject.toml](pyproject.toml).Recommended version is >3.9 and <3.12 . 
    - Follow the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) to install pyenv. 
    - Install specific Python version and create a virtualenv using below commands
    > **Warning for Windows Users:** The `pyenv` tool does not natively support Windows. You can opt for [pyenv-win](https://github.com/pyenv-win/pyenv-win) as an alternative, or use [miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/#) for setting up your virtual environment. However, it is advisable to set up [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to avoid any compatibility issues and have a smoother experience.

```bash
pyenv install 3.11.0
pyenv virtualenv  3.11.0 learn_ai
pyenv shell learn_ai
```

3. Install Dependencies

```bash
pip install poetry==1.6.1
poetry install --no-cache
```
4. Start jupyter notebook, when the instllation is complete. 

```bash
jupyter-lab
```

or 
```bash
jupyter
```

5. To Run the Notebooks select the kernal `learn_ai` in jupyter-notebook. 

### Running with Colab 
Add tocolab to the domain open a Github notebook directly in Colab i.e. replacing https://github.com with https://githubtocolab.com. 

Manually install all dependencies by adding them to “pip install” at the start of the notebook — for instance:

```bash
!pip install tiktoken voyager
```

Continue with the notebook!

