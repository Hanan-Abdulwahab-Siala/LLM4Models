#!/bin/bash -l

#SBATCH --job-name=LLM4Models
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=/scratch/users/%u/javapy-gradio-%j.out
#SBATCH --error=/scratch/users/%u/javapy-gradio-%j.err

set -e

# --------------------------------------------------
# LLM4Models - Gradio
# --------------------------------------------------

export PYTHONNOUSERSITE=1
export GRADIO_SERVER_PORT=7860

echo "========================================"
echo "LLM4Models - Gradio"
echo "========================================"

echo
echo "Compute node:"
hostname

echo
echo "Slurm job information:"
echo "Job ID                  : ${SLURM_JOB_ID:-not-set}"
echo "Node                    : ${SLURMD_NODENAME:-$(hostname)}"
echo "CUDA_VISIBLE_DEVICES    : ${CUDA_VISIBLE_DEVICES:-not-set}"
echo "Gradio port             : $GRADIO_SERVER_PORT"

# --------------------------------------------------
# GPU
# --------------------------------------------------

echo
echo "========================================"
echo "GPU"
echo "========================================"

if ! command -v nvidia-smi >/dev/null 2>&1; then
   echo "ERROR: nvidia-smi is not available."
   exit 1
fi

nvidia-smi

# --------------------------------------------------
# CUDA
# --------------------------------------------------

echo
echo "========================================"
echo "Loading CUDA"
echo "========================================"

module load cuda

echo
echo "CUDA module loaded."

# --------------------------------------------------
# Python environment
# --------------------------------------------------

echo
echo "========================================"
echo "Python environment"
echo "========================================"

cd "$HOME/LLM4Models"

if [ ! -f "$HOME/venvs/bin/activate" ]; then
   echo "ERROR: Python virtual environment not found:"
   echo "$HOME/venvs/bin/activate"
   exit 1
fi

. "$HOME/venvs/bin/activate"

echo
echo "Python:"
python --version

echo
echo "Python executable:"
which python

echo
echo "Virtual environment:"
echo "${VIRTUAL_ENV:-not-set}"

if [ "$(which python)" != "$HOME/venvs/bin/python" ]; then
   echo
   echo "ERROR: ~/venvs is not active."
   echo "Expected:"
   echo "$HOME/venvs/bin/python"
   echo
   echo "Found:"
   echo "$(which python)"
   exit 1
fi

# --------------------------------------------------
# PyTorch information
# --------------------------------------------------

echo
echo "========================================"
echo "PyTorch"
echo "========================================"

python -c "
import torch
print('PyTorch:', torch.__version__)
print('PyTorch CUDA:', torch.version.cuda)
print('GPU count:', torch.cuda.device_count())
"

# --------------------------------------------------
# Gradio port
# --------------------------------------------------

echo
echo "========================================"
echo "Checking Gradio port"
echo "========================================"

if command -v ss >/dev/null 2>&1; then
   if ss -ltn | grep -q ":${GRADIO_SERVER_PORT} "; then
      echo
      echo "ERROR: Port $GRADIO_SERVER_PORT is already in use."
      echo "Node: $(hostname)"
      echo
      ss -ltnp | grep ":${GRADIO_SERVER_PORT} " || true
      exit 1
   fi
fi

echo "Port $GRADIO_SERVER_PORT is available."

# --------------------------------------------------
# Application
# --------------------------------------------------

echo
echo "========================================"
echo "Checking application"
echo "========================================"

if [ ! -f "$HOME/LLM4Models/app.py" ]; then
   echo "ERROR: app.py was not found."
   echo "$HOME/LLM4Models/app.py"
   exit 1
fi

echo "Application found:"
echo "$HOME/LLM4Models/app.py"

# --------------------------------------------------
# Start Gradio
# --------------------------------------------------

echo
echo "========================================"
echo "Starting Gradio"
echo "========================================"

echo
echo "Compute node:"
hostname

echo
echo "Slurm Job ID:"
echo "${SLURM_JOB_ID:-not-set}"

echo
echo "Gradio port:"
echo "$GRADIO_SERVER_PORT"

echo
echo "========================================"
echo "Windows tunnel command"
echo "========================================"

echo

echo "for /f \"delims=\" %N in ('ssh -m hmac-sha2-512 ${USER}@hpc.create.kcl.ac.uk \"squeue -j $SLURM_JOB_ID -h -o %%N\"') do ssh -m hmac-sha2-512 -N -L 7860:%N:7860 ${USER}@hpc.create.kcl.ac.uk"
echo
echo "Then open:"
echo
echo "http://localhost:7860"

echo
echo "========================================"
echo "Running LLM4Models"
echo "========================================"

echo

python app.py
# --------------------------------------------------


