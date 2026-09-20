#!/bin/bash -l

#SBATCH --job-name=LLM4Modles
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=/scratch/users/%u/javapy-%j.out
#SBATCH --error=/scratch/users/%u/javapy-%j.err

export PYTHONNOUSERSITE=1

set -e

echo "========================================"
echo "LLM4Models - KCL GPU Job"
echo "========================================"

echo
echo "Compute node:"
hostname

# --------------------------------------------------
# Check GPU
# --------------------------------------------------

echo
echo "Checking GPU..."

if ! nvidia-smi >/dev/null 2>&1; then
    echo
    echo "ERROR: No GPU is available on this node."
    echo "The job will not continue."
    echo
    exit 1
fi

echo
echo "GPU available:"
nvidia-smi --query-gpu=name,memory.total --format=csv

# --------------------------------------------------
# Load CUDA
# --------------------------------------------------

echo
echo "Loading CUDA..."
module load cuda

# --------------------------------------------------
# Project
# --------------------------------------------------

cd "$HOME/LLM4Models"

source ~/venvs/bin/activate

# --------------------------------------------------
# Python
# --------------------------------------------------

echo
echo "Python:"
python --version

echo
echo "Python executable:"
which python

# --------------------------------------------------
# PyTorch / CUDA check
# --------------------------------------------------

echo
echo "Checking PyTorch CUDA..."

python -c "
import torch

print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('CUDA version:', torch.version.cuda)

if not torch.cuda.is_available():
    print()
    print('ERROR: PyTorch cannot access the allocated GPU.')
    print('The job will not continue.')
    raise SystemExit(1)

print('GPU:', torch.cuda.get_device_name(0))
"

# --------------------------------------------------
# Run Analyzer
# --------------------------------------------------

echo
echo "Running inference..."

# --------------------------------------------------
# Choose ONE command below starting with python and uncomment it.
# --------------------------------------------------
##### UML Extraction
# For a Java/Python file:
python analyze.py input/sample.java --language Java --task "UML" --model-version 1 --model-type "LoRA Adapter"
#
# python analyze.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter"
# 
# python analyze.py input/sample.java --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"
#
# python analyze.py input/sample.py --language Python --task "UML" --model-version 1 --model-type "LoRA Adapter"
#
# python analyze.py input/sample.py --language Python --task "UML" --model-version 2 --model-type "LoRA Adapter"
# --------------------------------------------------
# For Directory:
#
# python analyze.py input/ --language Java --task "UML" --model-version 2 --model-type "LoRA Adapter" --uml-detail "Detailed Class Diagram" --uml-parameters "Methods Only" --uml-format "PNG"
#
# Where choices are:
#
# --language field includes Java or Python,
# --task field "UML".
# --model-version field includes 1, 2, 3, or 4.
# --model-type field includes "LoRA Adapter" or "Full Model".
# --uml-detail field includes "Detailed Class Diagram" and "Outline Class Diagram".
#
# If you choose --uml-detail "Detailed Class Diagram" only, you can include: 
# --uml-parameters "Methods Only"
# --uml-parameters "Methods with Parameter Names and Types"
# --uml-parameters "Methods with Parameter Types"
#
# And if you choose --uml-detail "Outline Class Diagram", please do not select --uml-parameters.
#
# You can choose the --uml-format field from "PNG", "PDF", and "SVG".
# --------------------------------------------------
# Default values are:
#
# Diagram type: Detailed Class Diagram
# Parameters: Methods Only
# Format: PNG
#
# --------------------------------------------------
# --------------------------------------------------
##### OCL Extraction
#
# python analyze.py input/sample.java --language Java --task "OCL" --model-version 1 --model-type "LoRA Adapter"
#
# python analyze.py input/sample.java --language Java --task "OCL" --model-version 2 --model-type "LoRA Adapter"
#
# python analyze.py input/sample.py --language Python --task "OCL" --model-version 1 --model-type "LoRA Adapter"
#
# python analyze.py input/sample.py --language Python --task "OCL" --model-version 2 --model-type "LoRA Adapter"
#
# Where choices are:
#
# --language field includes Java or Python,
#
# --task field "OCL".
#
# --model-version field includes 1 or 2.
#
# --model-type field includes "LoRA Adapter" or "Full Model".
# --------------------------------------------------
# --------------------------------------------------
echo
echo "========================================"
echo "Job completed successfully"
echo "========================================"
# --------------------------------------------------
