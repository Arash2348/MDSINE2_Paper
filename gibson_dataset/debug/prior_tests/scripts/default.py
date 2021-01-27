"""
    Author: Younhun Kim
    A re-organization of step_5_infer_mdsine2.py for easier modification of parameters.
"""

import os
import mdsine2 as md2
from mdsine2.names import STRNAMES
from gibson_dataset.debug.prior_tests.scripts.base.infer_mdsine2 import create_config, run_mdsine
import logging
import argparse


def parse_args():
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument(
        '--study_path', type=str, dest='study_path', required=True,
        help='Path to the dataset\'s study object (pickle).'
    )
    parser.add_argument(
        '--seed', type=int, dest='seed', required=True,
        help='Seed for randomness'
    )
    parser.add_argument(
        '--basepath', type=str, dest='basepath', required=True,
        help='The directory path to output to, not including the study name itself.'
    )
    parser.add_argument(
        '--burnin', '-nb', type=int, dest='burnin',
        help='How many burn-in Gibb steps for Markov Chain Monte Carlo (MCMC)'
    )
    parser.add_argument(
        '--n-samples', '-ns', type=int, dest='n_samples',
        help='Total number Gibb steps to perform during MCMC inference'
    )
    parser.add_argument(
        '--checkpoint', '-c', type=int, dest='checkpoint',
        help='How often to write the posterior to disk. Note that `--burnin` and ' \
             '`--n-samples` must be a multiple of `--checkpoint` (e.g. checkpoint = 100, ' \
             'n_samples = 600, burnin = 300)'
    )
    parser.add_argument(
        '--multiprocessing', '-mp', type=int, dest='multiprocessing',
        help='If 1, run the inference with multiprocessing. Else run on a single process',
        default=0
    )
    return parser.parse_args()


def load_settings(cfg: md2.config.MDSINE2ModelConfig, study: md2.Study):
    n_taxa = len(study.taxa)

    # ====== Indicator priors ======
    interaction_prior = 'weak-agnostic'
    perturbation_prior = 'weak-agnostic'

    # ====== Negative binomial params ======
    negbin_a0 = 1e-2
    negbin_a1 = 1e-4
    cfg.set_negbin_params(negbin_a0, negbin_a1)

    # Set the sparsities
    cfg.INITIALIZATION_KWARGS[STRNAMES.CLUSTER_INTERACTION_INDICATOR_PROB]['hyperparam_option'] = interaction_prior
    cfg.INITIALIZATION_KWARGS[STRNAMES.PERT_INDICATOR_PROB]['hyperparam_option'] = perturbation_prior

    # Change the cluster initialization to no clustering if there are less than 30 taxa
    if n_taxa <= 30:
        logging.info('Since there are fewer than 30 taxa, we set the initialization of the clustering to `no-clusters`')
        cfg.INITIALIZATION_KWARGS[STRNAMES.CLUSTERING]['value_option'] = 'no-clusters'

    return cfg


def main():
    args = parse_args()

    # Load dataset
    logging.info('Loading dataset {}'.format(args.study_path))
    study = md2.Study.load(args.study_path)
    md2.seed(args.seed)

    # Load the model parameters
    output_basepath = os.path.join(args.basepath, study.name)
    os.makedirs(output_basepath, exist_ok=True)
    md2.config.LoggingConfig(level=logging.INFO, basepath=output_basepath)
    cfg = create_config(output_basepath,
                        negbin_a1=0.,  # to set in load_settings
                        negbin_a0=0.,  # to set in load_settings
                        seed=args.seed,
                        burnin=args.burnin,
                        n_samples=args.n_samples,
                        checkpoint=args.checkpoint,
                        multithreaded=args.multiprocessing)
    load_settings(cfg, study)

    # Run inference.
    run_mdsine(cfg, study)


if __name__ == "__main__":
    main()
