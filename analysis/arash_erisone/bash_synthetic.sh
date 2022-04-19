#!/bin/bash

# Path to MDSINE2_Paper code and to Synthetic Data Output
MDSINE2_PAPER_CODE_PATH=${MDSINE2_PAPER_CODE_PATH:-"/home/arash/MDSINE2_Arash_Paper"}
MDSINE2_OUTPUT_PATH="${MDSINE2_PAPER_CODE_PATH}/analysis/output/gibson"
PREPROCESSED_PATH="${MDSINE2_PAPER_CODE_PATH}/analysis/output/gibson/preprocessed"

# Conda environment
ENVIRONMENT_NAME="mdsine2"
# Queues, memory, and numpy of cpus
QUEUE="normal" #Switch to short for fast runs on ErisTwo
MEM="8000"
N_CPUS="1"

# Have the first argument be the sparsity we are running with. Default to strong sparse
DEFAULT_IND_PRIOR="strong-sparse"
IND_PRIOR=${1:-$DEFAULT_IND_PRIOR}

# NOTE: THESE PATHS MUST BE RELATIVE TO `MDSINE2_PAPER_CODE_PATH`
NEGBIN="${MDSINE2_OUTPUT_PATH}/negbin/replicates/mcmc.pkl"
BURNIN="10"
N_SAMPLES="30"
CHECKPOINT="10"
MULTIPROCESSING="0"

#New Paramaters for Synthetic
A0_LEVEL_LOW=".000001"
A1_LEVEL_LOW=".000003"
QPCR_LEVEL_LOW=".0001"

A0_LEVEL_MED=".00001"
A1_LEVEL_MED=".0250"
QPCR_LEVEL_MED=".0225"

A0_LEVEL_HIGH=".0001"
A1_LEVEL_HIGH=".09"
QPCR_LEVEL_HIGH=".09"



#/PHShome/as1010/MDSINE2_Paper/analysis/output/gibson/mdsine2_as1010/fixed_clustering/healthy-seed0-strong-sparse/mcmc.pkl
#Acquire health dataset - only dataset used for testing
HEALTHY_DATASET="${PREPROCESSED_PATH}/mcmc_real_use.pkl"

echo "Default parameters"
#Set current base paths for testing
BASEPATH="${MDSINE2_OUTPUT_PATH}/mdsine2_as1010_syn_run"
FIXED_BASEPATH="${MDSINE2_OUTPUT_PATH}/mdsine2_as1010_syn_run/fixed_clustering"

#Currently working with two seeds for testing
HEALTHY_SEED0="healthy-seed0-${IND_PRIOR}"
HEALTHY_SEED1="healthy-seed1-${IND_PRIOR}"

#Print addresses
echo $HEALTHY_SEED0
echo $BASEPATH
echo $FIXED_BASEPATH

# Healthy
# -------
python scripts/python_lsf_syn.py \
    --dataset $HEALTHY_DATASET \
    --negbin $NEGBIN \
    --seed 0 \
    --a0-level-low $A0_LEVEL_LOW \
    --a1-level-low $A1_LEVEL_LOW \
    --qpcr-level-low $QPCR_LEVEL_LOW \
    --a0-level-med $A0_LEVEL_MED \
    --a1-level-med $A1_LEVEL_MED \
    --qpcr-level-med $QPCR_LEVEL_MED \
    --a0-level-high $A0_LEVEL_HIGH \
    --a1-level-high $A1_LEVEL_HIGH \
    --qpcr-level-high $QPCR_LEVEL_HIGH \
    --burnin $BURNIN \
    --n-samples $N_SAMPLES \
    --checkpoint $CHECKPOINT \
    --rename-study $HEALTHY_SEED0 \
    --output-basepath $BASEPATH \
    --environment-name $ENVIRONMENT_NAME \
    --code-basepath $MDSINE2_PAPER_CODE_PATH \
    --queue $QUEUE \
    --memory $MEM \
    --n-cpus $N_CPUS \
#
#python scripts/python_lsf_syn.py \
#    --dataset $HEALTHY_DATASET \
#    --negbin $NEGBIN \
#    --seed 1 \
#    --a0-level $A0_LEVEL \
#    --a1-level $A1_LEVEL \
#    --qpcr-level $QPCR_LEVEL \
#    --burnin $BURNIN \
#    --n-samples $N_SAMPLES \
#    --checkpoint $CHECKPOINT \
#    --rename-study $HEALTHY_SEED1 \
#    --output-basepath $BASEPATH \
#    --environment-name $ENVIRONMENT_NAME \
#    --code-basepath $MDSINE2_PAPER_CODE_PATH \
#    --queue $QUEUE \
#    --memory $MEM \
#    --n-cpus $N_CPUS \


#Previous paramaters before changing:
#    --dataset $HEALTHY_DATASET \
#    --negbin $NEGBIN \
#    --seed 1 \
#    --burnin $BURNIN \
#    --n-samples $N_SAMPLES \
#    --checkpoint $CHECKPOINT \
#    --multiprocessing $MULTIPROCESSING \
#    --rename-study $HEALTHY_SEED1 \
#    --output-basepath $BASEPATH \
#    --fixed-output-basepath $FIXED_BASEPATH \
#    --environment-name $ENVIRONMENT_NAME \
#    --code-basepath $MDSINE2_PAPER_CODE_PATH \
#    --queue $QUEUE \
#    --memory $MEM \
#    --n-cpus $N_CPUS \
#    --interaction-ind-prior $INTERACTION_IND_PRIOR \
#    --perturbation-ind-prior $PERTURBATION_IND_PRIOR

#new