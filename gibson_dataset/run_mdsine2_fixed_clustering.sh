#!/bin/bash

NEGBIN="../output/negbin/replicates/mcmc.pkl"
SEED="0"
BURNIN="5000"
N_SAMPLES="15000"
CHECKPOINT="100"
MULTIPROCESSING="0"
INTERACTION_IND_PRIOR="strong-sparse"
PERTURBATION_IND_PRIOR="strong-sparse"
BASEPATH="../output/mdsine2/fixed_clustering"

echo "Running fixed clustering inference of MDSINE2"
echo "Writing files to ${BASEPATH}"

# Healthy cohort
# --------------
python ../step_5_infer_mdsine2.py \
    --input ../processed_data/gibson_healthy_agg_taxa_filtered.pkl \
    --negbin $NEGBIN \
    --seed $SEED \
    --burnin $BURNIN \
    --n-samples $N_SAMPLES \
    --checkpoint $CHECKPOINT \
    --multiprocessing $MULTIPROCESSING \
    --basepath $BASEPATH \
    --fixed-clustering ../output/mdsine2/healthy-seed0/mcmc.pkl \
    --interaction-ind-prior $INTERACTION_IND_PRIOR \
    --perturbation-ind-prior $PERTURBATION_IND_PRIOR
python ../step_6_visualize_mdsine2.py \
    --chain  "${BASEPATH}/healthy/mcmc.pkl" \
    --output-basepath "${BASEPATH}/healthy/posterior" \
    --fixed-clustering 1

# UC cohort
# ---------
python ../step_5_infer_mdsine2.py \
    --input ../processed_data/gibson_uc_agg_taxa_filtered.pkl \
    --negbin $NEGBIN \
    --seed $SEED \
    --burnin $BURNIN \
    --n-samples $N_SAMPLES \
    --checkpoint $CHECKPOINT \
    --multiprocessing $MULTIPROCESSING \
    --basepath $BASEPATH \
    --fixed-clustering ../output/mdsine2/uc-seed0/mcmc.pkl \
    --interaction-ind-prior $INTERACTION_IND_PRIOR \
    --perturbation-ind-prior $PERTURBATION_IND_PRIOR
python ../step_6_visualize_mdsine2.py \
    --chain  "${BASEPATH}/uc/mcmc.pkl" \
    --output-basepath "${BASEPATH}/uc/posterior" \
    --fixed-clustering 1