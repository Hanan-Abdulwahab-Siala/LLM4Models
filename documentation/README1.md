## 1) Running Via Gradio Web Interface

The Gradio interface can be used to:

* Select the model version
* Select LoRA or full model
* Enter Java/Python code
* Run the extraction program
* View UML class diagrams
* View OCL specifications

The following instructions describe how to run the application on a remote GPU/HPC provider and access the Gradio interface from your local computer.

> **Important:** The commands for requesting GPU resources, activating environments, and connecting to compute nodes depend on your HPC/GPU provider. The examples below use **SLURM**, which is commonly used on HPC systems. A KCL-specific example is provided where applicable.

---

#### 1. Connect to the GPU/HPC Provider

From your local computer, connect to the remote GPU/HPC server using SSH:

```bash
ssh -m hmac-sha2-512 USERNAME@HPC_HOST
```

Replace:

* `USERNAME` with your account username on the HPC/GPU provider.
* `HPC_HOST` with the hostname of the remote HPC/GPU server.

For example:

```bash
ssh -m hmac-sha2-512 username@hpc.example.org
```

After connecting successfully, you should see a shell prompt on the HPC login node, similar to:

```bash
username@hpc-login:~$
```

> **Note:** You must have an account and SSH access to the HPC/GPU provider before running this command. The hostname, username, authentication method, and SSH options may differ between providers.

**KCL example:**

For users of the KCL CREATE HPC system, the connection may look like:

```bash
ssh -m hmac-sha2-512 k12345@hpc.create.kcl.ac.uk
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

```text
extract.py
app.py
input/
...
```

You can also check your current directory:

```bash
pwd
```

> **Note:** The project directory may be different depending on where you cloned or copied the project.

---

#### 3. Verify the Input File Exists

Check the input file:

```bash
ls -lh input/sample.java
```

or:

```bash
ls -lh input/sample.py
```

You can also inspect the input file:

```bash
cat input/sample.java
```

or:

```bash
cat input/sample.py
```

---

#### 4. Request a GPU Resource

If your HPC provider uses SLURM, request a GPU resource.

For example:

```bash
srun --partition=gpu \
     --gres=gpu:1 \
     --time=04:00:00 \
     --cpus-per-task=4 \
     --mem=32G \
     --pty /bin/bash -l
```

The exact command depends on your HPC provider. The partition name, GPU specification, time limit, CPU allocation, and memory requirements may be different.

After the resources have been allocated, SLURM may display something similar to:

```text
srun: job 12345678 has been allocated resources
```

The number `12345678` is the **SLURM job ID**. Keep this number because it can be used later when creating the SSH tunnel.

Check that the GPU is available:

```bash
nvidia-smi
```

If required by your HPC provider, load CUDA:

```bash
module load cuda
```

> **KCL example:** The SLURM command above is suitable as an example for a KCL CREATE environment, but users should follow the current resource requirements and partition configuration provided by their HPC administrator.

---

#### 5. Activate the Python Virtual Environment

Activate the Python virtual environment:

```bash
. ~/venvs/bin/activate
```

Check the Python version:

```bash
python --version
```

Check where Python is coming from:

```bash
which python
```

It should point to a Python executable inside your virtual environment, for example:

```text
/home/username/venvs/bin/python
```

> **Note:** The location of the virtual environment may be different on your system. Use the virtual environment created for the project.

---

#### 6. Run the Gradio Program

Run the Gradio application:

```bash
python app.py
```

The application should start using the port configured in `app.py`.

---

#### 7. Create an SSH Tunnel

Open a **second CMD window on your local Windows computer**.

The SSH tunnel forwards a port from your local computer to the port where the Gradio application is running on the HPC compute node.

There are two ways to identify the compute node: using the **SLURM job ID** or using the **SLURM job name**.

### Option A: Use the SLURM Job ID

If you know the SLURM job ID, use:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -j JOB_ID -h -o %%N"') do ssh -m hmac-sha2-512 -N -L LOCAL_PORT:%N:REMOTE_PORT USERNAME@HPC_HOST
```

Replace:

* `USERNAME` → your HPC username
* `HPC_HOST` → your HPC login hostname
* `JOB_ID` → your SLURM job ID
* `LOCAL_PORT` → the port on your local computer
* `REMOTE_PORT` → the port used by the Gradio application

For example, if:

* the SLURM job ID is `12345678`
* the Gradio application uses port `7860`
* the local port is `7860`

use:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -j 12345678 -h -o %%N"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 USERNAME@HPC_HOST
```

> **Important:** `-j` means **job ID**. Only provide the numeric SLURM job ID after `-j`. Do **not** write the job name after `-j`.

### Option B: Use the SLURM Job Name

If you want to identify the job by its SLURM job name, use `-n`:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -n \"JOB_NAME\" -h -o %%N"') do ssh -m hmac-sha2-512 -N -L LOCAL_PORT:%N:REMOTE_PORT USERNAME@HPC_HOST
```

For example, if your SLURM job is named `Jupyter Lab`:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -n \"Jupyter Lab\" -h -o %%N"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 USERNAME@HPC_HOST
```

> **Recommendation:** Using the numeric SLURM job ID with `-j` is usually clearer and avoids problems caused by spaces or special characters in job names.

Keep this second CMD window open while using the Gradio application.

**KCL example:**

If your KCL SLURM job ID is `37241627`, your command would be:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 k12345@hpc.create.kcl.ac.uk "squeue -j 37241627 -h -o %%N"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 k12345@hpc.create.kcl.ac.uk
```

Notice that the command uses:

```text
squeue -j 37241627
```

and **not**:

```text
squeue -j Jupyter Lab 37241627
```

---

#### 8. Open the Gradio Application

Leave both windows open:

1. The HPC terminal running `python app.py`
2. The local Windows CMD window running the SSH tunnel

Then open a web browser on your local computer and enter:

```text
http://localhost:7860
```

Your Gradio application should open in the browser.

---

