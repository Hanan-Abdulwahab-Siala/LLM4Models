## 3) Running Using KCL CREATE HPC Workflow with Gradio

We provide an optional KCL CREATE script to run the project in an HPC/GPU environment using a Gradio interface.

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

#### 4. Check the SLURM Script and Make the Script Executable

Run:

```bash
cat KCL/run_kcl_gradio.sh
```

Then:

```bash
chmod +x KCL/run_kcl_gradio.sh
```

Check the file:

```bash
ls -l KCL/run_kcl_gradio.sh
```

You should see executable permissions, for example:

```
-rwxr-xr-x ... run_kcl_gradio.sh
```
---

#### 5. Submit the SLURM Job

Submit the script using:

```bash
sbatch KCL/run_kcl_gradio.sh
```

You should receive something similar to:

```
Submitted batch job 12345678
```

The number is the **JOBID**. For example:

```
JOBID=12345678
```

Your JOBID will be different each time you submit a new job.

Wait until the job is running:

```bash
squeue -j 12345678
```
Your output will look like:
```bash
JOBID       PARTITION   NAME         USER    ST   NODELIST
12345678    gpu         LLM4Models   ...     R    gpu-node-42
```

---
#### 6. Open the SSH Tunnel

Now go to your Windows PC and open a **second CMD window**.

Use the **JOBID obtained in Step 5** to find the compute node running your SLURM job and create an SSH tunnel to the Gradio application.

The general command is:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -j JOB_ID -h -o %%N"') do ssh -m hmac-sha2-512 -N -L LOCAL_PORT:%N:REMOTE_PORT USERNAME@HPC_HOST
```

Replace:

* `USERNAME` → your HPC username
* `HPC_HOST` → your HPC login hostname
* `JOB_ID` → the SLURM job ID obtained in Step 5
* `LOCAL_PORT` → the port on your local computer, e.g. `7860`
* `REMOTE_PORT` → the port used by the Gradio application, e.g. `7860`

For example, if your JOBID is:

```text
12345678
```

and the Gradio application uses port `7860`, use:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 USERNAME@HPC_HOST "squeue -j 12345678 -h -o %%N"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 USERNAME@HPC_HOST
```

**KCL example:**

If your KCL username is `k12345`, your KCL HPC hostname is `hpc.create.kcl.ac.uk`, and your JOBID is `12345678`:

```cmd
for /f "delims=" %N in ('ssh -m hmac-sha2-512 k12345@hpc.create.kcl.ac.uk "squeue -j 12345678 -h -o %%N"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 k12345@hpc.create.kcl.ac.uk
```

> **Important:** When using `squeue -j`, provide **only the numeric JOBID**. Do not include the job name.

For example, this is **incorrect**:

```bash
squeue -j Jupyter Lab 12345678
```

The correct command is:

```bash
squeue -j 12345678
```

Keep this CMD window open while using the Gradio interface.

---

#### 7. Open Gradio in Your Browser

Once the SSH tunnel is active, open Chrome, Edge, Firefox, or another browser.

Go to:

```text
http://localhost:7860
```

The Gradio interface should appear.

---
