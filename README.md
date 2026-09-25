# LLM4Models

An LLM4Models project for extracting UML class diagrams and OCL specifications from both Java and Python code using a fine-tuned Mistral LLM.

The project provides:

- A command-line extractor
- A Gradio web interface
- LoRA adapter and full-model options
- Automatic GPU hardware detection
- Optional KCL CREATE HPC scripts for the project author's GPU workflow

---

## Project Structure

A typical project structure is:

```text
LLM4Models/
│
├── README.md
├── requirements.txt
│
├── extract.py
├── app.py
├── model_service.py
├── graphviz_service.py
│
├── input/
│   └── sample.java
│   └── sample.py
│
├── output/
│   └── output.txt
│
└── KCL/
    └── run_kcl_extract.sh
    └── run_kcl_gradio.sh

```

---

## Requirements

Recommended:

- Python 3.10+
- PyTorch
- Transformers
- PEFT
- Accelerate
- SentencePiece
- Safetensors
- Protobuf
- Huggingface_hub
- Gradio
- NVIDIA GPU with CUDA support for GPU inference

---

## Installation

Clone the repository:

```bash
git clone https://github.com/HA-Siala/LLM4Models.git
cd LLM4Models
```

Create a virtual environment:

```bash
python3 -m venv ~/venvs
```

Activate the virtual environment.

**Linux / macOS**

```bash
source ~/venvs/bin/activate

```

**Windows**

```bash
. ~/venvs/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then, we need to create a Conda environment for Graphviz
```bash
cd ~
conda create -n graphviz-env -c conda-forge graphviz
```
Then type y, and then activate the Graphviz environment:
```bash
conda activate graphviz-env
```

Check the location of dot:
```bash
which dot
```
You should see:
```bash
/users/k12345/.conda/envs/graphviz-env/bin/dot
```
Then verify the version:
```bash
dot -V
```
You should see:
```bash
dot - graphviz version 12.x.x
```
Then leave the Graphviz Conda environment:
```bash
conda deactivate
```
And activate your Python virtual environment:
```bash
. ~/venvs/bin/activate
```
And verify Python:
```bash
which python
```
You should see:
```bash
~/venvs/bin/python
```
Install the Python Graphviz package while ~/venvs is activated; run:
```bash
pip install graphviz
```
You can verify the installation by running:
```bash
pip show graphviz
```

And finally, configure the location of dot in LLM4Models/graphviz_service.py by explicitly telling the Graphviz Python package where the dot executable is located. Please modify the following code in LLM4Models/graphviz_service.py as:

```bash
DEFAULT_GRAPHVIZ_DOT = ("/users/<USERNAME>/.conda/envs/graphviz-env/bin/dot") 
```
where <USERNAME> is the username of the account running the program.

You can find the exact path automatically with:

```bash
conda activate graphviz-env
which dot
```
You should see:

```bash
/users/k12345/.conda/envs/graphviz-env/bin/dot
```
Take it and put it in LLM4Models/graphviz_service.py as:
```bash
DEFAULT_GRAPHVIZ_DOT = ("/users/k12345/.conda/envs/graphviz-env/bin/dot")
```
---
## Running

### 1. [Running via Gradio Web Interface](./documentation/README1.md)
### 2. [Running from the Command-Line](./documentation/README2.md)
### 3. [Running Using KCL CREATE HPC Workflow with Gradio](./documentation/README3.md)
### 4. [Running Using KCL CREATE HPC Workflow without Gradio](./documentation/README4.md)

If you are not using the KCL CREATE environment, ignore the HPC scripts (3 and 4) and run the project in a standard Python environment.

---

## Supported Models

The project uses models hosted on Hugging Face. Make sure the required model repositories are accessible from your environment.

Model identifiers used by the project include:

### Base Model

- 👉 [mistralai/Mistral-7B-v0.3](https://huggingface.co/mistralai/Mistral-7B-v0.3)

### Fine-tuned Models
- 👉 [models](./models/) contains fine-tuned models to extract UML and OCL representations from Java and Python programs.
The full-model workflow loads the complete checkpoint directly.

Please review the applicable model licenses and terms before redistributing model files or using them commercially.

---

## Contact

**Student:** Hanan Abdulwahab Siala &nbsp;&nbsp;&nbsp;&nbsp; **Supervisor:** Kevin Lano  
hanan.siala@kcl.ac.uk &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; kevin.lano@kcl.ac.uk

King's College London
