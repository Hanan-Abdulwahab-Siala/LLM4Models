## 2) Running from the Command-Line 

Please follow these instructions:  

#### 1. Connect to the GPU Provider

From your local computer, connect to the remote GPU/HPC server using SSH. For example:

```bash
ssh -m hmac-sha2-512 USERNAME@HPC_HOST
```

Replace:

- USERNAME with your account username on the HPC/GPU provider.
- HPC_HOST with the hostname of the remote HPC/GPU server.

After connecting successfully, you should see a shell prompt on the HPC login node, similar to:

```bash
USERNAME@HPC_LOGIN_NODE:~$
```

For example, if your provider gives you the username `k12345` and the login hostname `hpc.example.org`:

```bash
ssh -m hmac-sha2-512 k12345@hpc.example.org
```

> **Note:** You must have an account and SSH access to the HPC/GPU provider before running this command. The hostname, username, authentication method, and SSH options may differ between providers.

---

#### 2. Go to the Project Directory

Move into the LLM4Models project:

```bash
cd ~/LLM4Models
```

Check that the project is there:

```bash
ls
```

You should see files such as:

```
extract.py
app.py
input/
...
```

You can also check your current directory:

```bash
pwd
```
---

#### 3. Verify the Input File Exists

Check the input file:

```bash
ls -lh input/sample.java
or
ls -lh input/sample.py
```

You can also test:

```bash
cat input/sample.java
or
cat input/sample.py
```
---

#### 4. Ask for a GPU from the GPU Provider
For example, in KCL, we use:

```bash
srun --partition=gpu \
     --gres=gpu:1 \
     --time=04:00:00 \
     --cpus-per-task=4 \
     --mem=32G \
     --pty /bin/bash -l
```
Then:

```bash
nvidia-smi
```
And then:

```bash
module load cuda
```

---

#### 5. Activate the Python Virtual Environment
Activate the virtual environment:

```bash
. ~/venvs/bin/activate
```

Check Python:

```bash
python --version
```

Check where Python is coming from:

```bash
which python
```

It should point to something similar to:

```
.../venvs/bin/python
```
---

#### 6. Run the Program

Run the extract program using one of the following:

##### UML Extraction
For a Java/Python file:
```bash
python extract.py input/sample.java --language Java --task "UML" --model-version 1 --model-type "LoRA Adapter"

python extract.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter"

python extract.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"

python extract.py input/sample.py --language Python --task "UML" --model-version 1 --model-type "LoRA Adapter"

python extract.py input/sample.py --language Python --task "UML" --model-version 2 --model-type "LoRA Adapter"
```

For Directory:
```bash
python extract.py input/ --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"
```

Where the choices are:

- --language field includes Java or Python.
- --task field: "UML".
- --model-version field includes 1, 2, 3, or 4.
- --model-type field includes "LoRA Adapter" or "Full Model".
- --uml-detail field includes "Detailed Class Diagram" and "Outline Class Diagram".

If you choose --uml-detail "Detailed Class Diagram" only, you can include: 
- --uml-parameters "Methods Only".
- --uml-parameters "Methods with Parameter Names and Types".
- --uml-parameters "Methods with Parameter Types".

If you choose --uml-detail "Outline Class Diagram", do not select --uml-parameters.

You can choose the --uml-format field from "PNG", "PDF", and "SVG".

Default values are:

- Diagram type: Detailed Class Diagram.
- Parameters: Methods Only.
- Format: PNG.

###### Generated Files

```text
output/
├── output.txt                # raw JSON response from the LLM
├── inference_metrics.txt     # inference metrics
├── Test1.UML                 # extracted UML classes
├── Test1.REL                 # extracted UML relationships
├── Test1.dot                 # Graphviz DOT source
└── Test1.png                 # Test1.png / .pdf / .svg — generated UML diagram
```

##### OCL Extraction
```bash
python extract.py input/sample.java --language Java --task "OCL" --model-version 1 --model-type "LoRA Adapter"

python extract.py input/sample.java --language Java --task "OCL" --model-version 2 --model-type "LoRA Adapter"

python extract.py input/sample.py --language Python --task "OCL" --model-version 1 --model-type "LoRA Adapter"

python extract.py input/sample.py --language Python --task "OCL" --model-version 2 --model-type "LoRA Adapter"
```
Where the choices are:

--language field includes Java or Python.

--task field: "OCL".

--model-version field includes 1 or 2.

--model-type field includes "LoRA Adapter" or "Full Model".

###### Generated Files

```text
output/
├── output.txt              # raw JSON response from the LLM
├── inference_metrics.txt   # inference metrics
├── Test1.OCL               # generated OCL specification
```
---

