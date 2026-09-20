## 2) Running from the Command-Line 

Please follow these instructions:  

#### 1. Connect to the GPU Provider

From your local computer, connect to the remote server, for example:

```bash
ssh -m hmac-sha2-512 k12345@hpc.create.kcl.ac.uk
```
After connecting, you should see a shell prompt on the HPC login node:
```bash
k12345@arc-hpc-login3:~$
```
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
analyze.py
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

Run the analyze program using one of the following:

##### UML Extraction
For a Java/Python file:
```bash
python analyze.py input/sample.java --language Java --task "UML" --model-version 1 --model-type "LoRA Adapter"

python analyze.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter"

python analyze.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"

python analyze.py input/sample.py --language Python --task "UML" --model-version 1 --model-type "LoRA Adapter"

python analyze.py input/sample.py --language Python --task "UML" --model-version 2 --model-type "LoRA Adapter"
```

For Directory:
```bash
python analyze.py input/ --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"
```

Where choices are:

--language field includes Java or Python,

--task field "UML".

--model-version field includes 1, 2, 3, or 4.

--model-type field includes "LoRA Adapter" or "Full Model".

--uml-detail field includes "Detailed Class Diagram" and "Outline Class Diagram".

If you choose --uml-detail "Detailed Class Diagram" only, you can include: 
--uml-parameters "Methods Only"
--uml-parameters "Methods with Parameter Names and Types"
--uml-parameters "Methods with Parameter Types"

And if you choose --uml-detail "Outline Class Diagram", please do not select --uml-parameters.

You can choose the --uml-format field from "PNG", "PDF", and "SVG".

Default values are:

Diagram type: Detailed Class Diagram
Parameters: Methods Only
Format: PNG

Generated files are:
output/output.txt
output/inference_metrics.txt
output/Test1.UML
output/Test1.REL
output/Test1.dot
output/Test1.png

##### OCL Extraction
```bash
python analyze.py input/sample.java --language Java --task "OCL" --model-version 1 --model-type "LoRA Adapter"

python analyze.py input/sample.java --language Java --task "OCL" --model-version 2 --model-type "LoRA Adapter"

python analyze.py input/sample.py --language Python --task "OCL" --model-version 1 --model-type "LoRA Adapter"

python analyze.py input/sample.py --language Python --task "OCL" --model-version 2 --model-type "LoRA Adapter"
```
Where choices are:

--language field includes Java or Python,

--task field "OCL".

--model-version field includes 1 or 2.

--model-type field includes "LoRA Adapter" or "Full Model".

Generated files are:
output/output.txt
output/inference_metrics.txt
output/Test1.OCL

---
