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
├── analyze.py
├── app.py
├── model_service.py
│
├── input/
│   └── sample.java
│   └── sample.py
│
├── output/
│   └── output.txt
│
└── KCL/
    └── run_kcl_analyze.sh
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

---
## Running

### 1. [Running via Gradio Web Interface](./documentation/README1.md)
### 2. [Running from the Command-Line](./documentation/README2.md)
### 3. [Running Using KCL CREATE HPC Workflow with Gradio](./documentation/README3.md)
### 4. [Running Using KCL CREATE HPC Workflow without Gradio](./documentation/README4.md)

If you are not using the KCL CREATE environment, you can ignore the HPC scripts (3 and 4) and run the project using the normal Python environment.

---

## Supported Models

The project uses models hosted on Hugging Face. You may need to make sure the required model repositories are accessible from your environment.

Model identifiers used by the project include:

### Base Model

- 👉 [mistralai/Mistral-7B-v0.3](https://huggingface.co/mistralai/Mistral-7B-v0.3)

### Fine-tuned Models
- 👉 [models](./models/) contains fine-tuned models to abstract UML and OCL representations from Java and Python programs.
The full-model workflow loads the complete checkpoint directly.

Please review the applicable model licenses and terms before redistributing model files or using them commercially.

---

## Credits

**Student:** Hanan Abdulwahab Siala &nbsp;&nbsp;&nbsp;&nbsp; **Supervisor:** Kevin Lano

---

## License

MIT License

---

## Contact

hanan.siala@kcl.ac.uk &nbsp;&nbsp;&nbsp;&nbsp; kevin.lano@kcl.ac.uk

King's College London
