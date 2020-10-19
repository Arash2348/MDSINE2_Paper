'''Keystoneness metric
'''

import numpy as np
import pandas as pd
import logging
import sys
import scipy.stats
import scipy.sparse
import scipy.spatial
import numba
import time
import collections
import h5py
import argparse

import pylab as pl

logging.basicConfig(level=logging.DEBUG)
subjset_filename = 'subjset.pkl'
growth_filename = 'growth.npy'
self_interactions_filename = 'self_interactions.npy'
interactions_filename = 'interactions.npy'
perturbationX_filename = 'perturbation{pidx}.npy'
limit_of_detection = 1e5

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--type', type=str, dest='keystoneness_type',
        help='What type of keystoneness to do. Options: `perturbation`, `leave-one-out`')
    parser.add_argument('--input-basepaths', type=str, dest='input_basepath',
        help='The path to find the growth, interaction, and perturbation traces')
    parser.add_argument('--output-basepath', type=str, dest='output_basepath',
        help='Where to save the outputs')
    parser.add_argument('--simulation-dt', type=float, dest='simulation_dt',
        help='Timesteps we go in during forward simulation', default=0.01)
    parser.add_argument('--leave-out', type=int, dest='leave_out',
        help='Index to leave out', default=None)
    parser.add_argument('--leave-out-table', type=str, dest='leave_out_table',
        help='File containing which ASVs to remove at each iteration', default=None)

    args = parser.parse_args()
    return args

class Result(pl.Saveable):

    def __init__(self, idx_removed, array):
        self.idx_removed = idx_removed
        self.array = array

class EfficientgLVDynamics(pl.BaseDynamics):

    def __init__(self, asvs, sim_max, growth, interactions, perturbations=None,
        perturbation_starts=None, perturbation_ends=None):
        '''
        '''
        pl.BaseDynamics.__init__(self, asvs=asvs)

        self.sim_max = sim_max

        self.growth = growth
        self.interactions = interactions
        self.perturbations = perturbations
        self.perturbation_starts = perturbation_starts
        self.perturbation_ends = perturbation_ends
        self._pert_intervals = None
        self._adjusted_growth = None

    def init_integration(self):

        self.growth = self.growth.reshape(-1,1)
        if self.perturbations is not None:
            self._adjust_growth = []
            for pert in self.perturbations:
                pert = pert.reshape(-1,1)
                self._adjust_growth.append(self.growth * (1 + pert))

    def integrate_single_timestep(self, x, t, dt):
        '''Integrate over a single step

        Parameters
        ----------
        x : np.ndarray((n,1))
            This is the abundance as a column vector for each ASV
        t : numeric
            This is the time point we are integrating to
        dt : numeric
            This is the amount of time from the previous time point we
            are integrating from
        '''
        growth = self.growth

        if self.perturbations is not None:

            # Initialize pert_intervals
            if self._pert_intervals is None:
                # float -> int
                # timepoint -> perturbation index

                self._pert_intervals = {}
                for pidx in range(len(self.perturbation_ends)):
                    start = self.perturbation_starts[pidx]
                    end = self.perturbation_ends[pidx]
                    rang = np.arange(start, end, step=dt)

                    for t in rang:
                        self._pert_intervals[t] = pidx
            
            if t-dt in self._pert_intervals:
                growth = self._adjust_growth[self._pert_intervals[t]]

        # Integrate
        logret = np.log(x) + (growth + self.interactions @ x) * dt
        ret = np.exp(logret).ravel()
        ret[ret >= self.sim_max] = self.sim_max
        return ret
    
    def finish_integration(self):
        self._pert_intervals = None
        self._adjusted_growth = None

def keystoneness_perturbation(chain_fname, fname, outfile_table, initial_conditions=None, 
    max_posterior=None):

    pass

# def keystoneness_knockdown():
#     pass

def keystoneness_leave_one_out_single(growth, self_interactions, interactions, dt,
    initial_conditions, output_basepath, asvs, leave_out_array, leave_out=None):
    '''Calculate the leave one out keystoneness

    Parameters
    ----------
    growth : np.ndarray (n_samples, n_asvs)
    self_interactions : np.ndarray (n_samples, n_asvs)
    interactions : np.ndarray (n_samples, n_asvs, n_asvs)
    dt : float
    initial_conditions : np.ndarray (n_asvs, )
        Assume that there are no zeros in here
    output_basepath : str
    leave_out : idx, None
        If None, leave nothing out
    asvs : pl.base.ASVSet
    leave_out_array : list(tuple(str))
        A list of asv names to remove at each index
    leave_out : int
        Which index to leave out
    '''
    mask = np.ones(growth.shape[1], dtype=bool)
    if leave_out == -1:
        leave_out = None
    if leave_out is not None:
        asvs_names = leave_out_array[leave_out]
        asvs_names = asvs_names.split(',')

        logging.info('Leave out {}: leaving asvs out {}'.format(leave_out, asvs_names))
        idxs = [asvs[asvname].idx for asvname in asvs_names]
        mask[idxs] = False

    initial_conditions = initial_conditions.ravel()[mask]

    growth = growth[:, mask]
    self_interactions = self_interactions[:, mask]
    if leave_out is not None:
        interactions = np.delete(interactions, idxs, 1)
        interactions = np.delete(interactions, idxs, 2)

    self_interactions = -np.absolute(self_interactions)
    for i in range(self_interactions.shape[1]):
        interactions[:, i, i] = self_interactions[:, i]

    n_samples = growth.shape[0]
    n_asvs = growth.shape[1]
    n_days = 20
    pred_matrix = np.zeros(shape=(n_samples, n_asvs), dtype=float)

    start_time = time.time()
    for gibb_step in range(n_samples):
        if gibb_step % 100 == 0:
            logging.info('{}/{}: {}'.format(gibb_step,n_samples, time.time()-start_time))
            start_time = time.time()
        dyn = EfficientgLVDynamics(
            asvs=asvs, 
            growth=growth[gibb_step], 
            interactions=interactions[gibb_step], sim_max=1e20)
        
        output = pl.dynamics.integrate(dynamics=dyn, initial_conditions=initial_conditions.reshape(-1,1),
            dt=0.1, n_days=n_days+dt, subsample=True, times=[0,n_days])
        pred_matrix[gibb_step] = output['X'][:, -1]

    if output_basepath[-1] != '/':
        output_basepath += '/'
    if leave_out is None:
        fname = output_basepath + 'base.npy'
    else:
        fname = output_basepath + 'leave_out{}.npy'.format(leave_out)

    ret = np.mean(pred_matrix, axis=0)
    np.save(fname, ret)


if __name__ == '__main__':

    # Load the inference parameters
    # -----------------------------
    args = parse_args()

    basepath = args.input_basepath
    if basepath[-1] != '/':
        basepath += '/'

    logging.info('Loading')
    subjset = pl.SubjectSet.load(basepath + subjset_filename)
    growth = np.load(basepath + growth_filename)
    self_interactions = np.load(basepath + self_interactions_filename)
    interactions = np.load(basepath + interactions_filename)
    perturbation0 = np.load(basepath + perturbationX_filename.format(pidx=0))
    perturbation1 = np.load(basepath + perturbationX_filename.format(pidx=1))
    perturbation2 = np.load(basepath + perturbationX_filename.format(pidx=2))
    perturbations = [perturbation0, perturbation1, perturbation2]

    logging.info('shapes')
    logging.info('growth {}'.format(growth.shape))
    logging.info('self_interactions {}'.format(self_interactions.shape))
    logging.info('interactions {}'.format(interactions.shape))
    logging.info('perturbation0 {}'.format(perturbation0.shape))
    logging.info('perturbation1 {}'.format(perturbation1.shape))
    logging.info('perturbation2 {}'.format(perturbation2.shape))

    pert_starts = [pert.start for pert in subjset.perturbations]
    pert_ends = [pert.end for pert in subjset.perturbations]

    # Make the initial conditions
    # ---------------------------
    initial_conditions = np.zeros(shape=(len(subjset), len(subjset.asvs)))
    for sidx, subj in enumerate(subjset):
        M = subj.matrix()['abs']
        tidx = np.searchsorted(subj.times, 1)
        initial_conditions[sidx] = M[:,tidx]

    initial_conditions = np.mean(initial_conditions, axis=0)
    initial_conditions[initial_conditions == 0] = limit_of_detection

    # Parse the leave out table
    # -------------------------
    f = open(args.leave_out_table, 'r')
    txt = f.read()
    f.close()
    lst = txt.split('\n')

    
    if args.keystoneness_type == 'leave-one-out':
        keystoneness_leave_one_out_single(
            growth=growth, self_interactions=self_interactions, interactions=interactions,
            dt=args.simulation_dt, initial_conditions=initial_conditions, 
            output_basepath=args.output_basepath, asvs=subjset.asvs, 
            leave_out_array=lst, leave_out=args.leave_out)
    elif args.keystoneness_type == 'perturbations':
        raise NotImplementedError('Not Implemented')
    else:
        raise ValueError('`type` ({}) not recognized'.format(args.keystoneness_type))