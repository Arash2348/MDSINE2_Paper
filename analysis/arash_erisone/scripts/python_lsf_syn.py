# '''
# All the arguments needed consist of the following:
#
# --input MCMC
# --rename_study
# --seeds
# --checkpoint
# --burn-in
# --n_points (gibb-steps)
# -- a0=a0_level,
# --a1=a1_level,
# ---qpcr_noise_scale=qpcr_level
# --negbin
# -q {queue}
# -n {cpus}
# -M {mem}
# '''

# Code Below -------------------

lsfstr = '''#!/bin/bash
#BSUB -J {jobname}
#BSUB -o {stdout_loc}
#BSUB -e {stderr_loc}
#BSUB -q {queue}
#BSUB -n {cpus}
#BSUB -M {mem}
#BSUB -R rusage[mem={mem}]
echo '---PROCESS RESOURCE LIMITS---'
ulimit -a
echo '---SHARED LIBRARY PATH---'
echo $LD_LIBRARY_PATH
echo '---APPLICATION SEARCH PATH:---'
echo $PATH
echo '---LSF Parameters:---'
printenv | grep '^LSF'
echo '---LSB Parameters:---'
printenv | grep '^LSB'
echo '---LOADED MODULES:---'
module list
echo '---SHELL:---'
echo $SHELL
echo '---HOSTNAME:---'
hostname
echo '---GROUP MEMBERSHIP (files are created in the first group listed):---'
groups
echo '---DEFAULT FILE PERMISSIONS (UMASK):---'
umask
echo '---CURRENT WORKING DIRECTORY:---'
pwd
echo '---DISK SPACE QUOTA---'
df .
echo '---TEMPORARY SCRATCH FOLDER ($TMPDIR):---'
echo $TMPDIR
# Load the environment
module load anaconda/4.8.2
source activate {environment_name}
cd {code_basepath}



# Run the synthetic generation 
# -------------
mdsine2 synthetic\
    --input {dset_fileloc} \
    --negbin {negbin_run} \
    --seed {seed} \
    --a0-level {a0_level} \
    --a1-level {a1_level} \
    --qpcr-level {qpcr_level} \
    --burnin {burnin} \
    --n-samples {n_samples} \
    --checkpoint {checkpoint} \
    --rename-study {rename_study} \
    --output-basepath {basepath} \


'''

import mdsine2 as md2
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=__doc__)

    # Synthetic Parameters
    parser.add_argument('--dataset', '-d', type=str, dest='dataset',
        help='This is the Gibson dataset we are performing inference on')
    parser.add_argument('--negbin', type=str, dest='negbin',
                        help='This is the MCMC object that was run to learn a0 and a1')
    parser.add_argument('--a0-level', '-a0', type=float, dest='a0_level',
                        help='This is the a0-noise-level for the synthetic data-generation parameter')
    parser.add_argument('--a1-level', '-a1', type=float, dest='a1_level',
                        help='This is the a1-noise-level for the synthetic data-generation parameter')
    parser.add_argument('--qpcr-level', '-qpcr', type=float, dest='qpcr_level',
                        help='This is the qpcr-noise-level for the synthetic data-generation parameter')
    parser.add_argument('--seed', '-s', type=int, dest='seed',
                        help='This is the seed to initialize the inference with')
    parser.add_argument('--burnin', '-nb', type=int, dest='burnin',
                        help='How many burn-in Gibb steps for Markov Chain Monte Carlo (MCMC)')
    parser.add_argument('--n-samples', '-ns', type=int, dest='n_samples',
                        help='Total number Gibb steps to perform during MCMC inference')
    parser.add_argument('--checkpoint', '-c', type=int, dest='checkpoint',
                        help='How often to write the posterior to disk. Note that `--burnin` and ' \
                             '`--n-samples` must be a multiple of `--checkpoint` (e.g. checkpoint = 100, ' \
                             'n_samples = 600, burnin = 300)')
    parser.add_argument('--lsf-basepath', '-l', type=str, dest='lsf_basepath',
                        help='This is the basepath to save the lsf files', default='lsf_files/')
    parser.add_argument('--rename-study', type=str, dest='rename_study',
                        help='Rename the name of the study to this', default=None)
    parser.add_argument('--output-basepath', type=str, dest='basepath',
                        help='Output of the model', default=None)

    # Erisone Parameters
    parser.add_argument('--environment-name', dest='environment_name', type=str,
                        help='Name of the conda environment to activate when the job starts')
    parser.add_argument('--code-basepath', type=str, dest='code_basepath',
                        help='Where the `run_cross_validation` script is located')
    parser.add_argument('--queue', '-q', type=str, dest='queue',
                        help='ErisOne queue this job gets submitted to')
    parser.add_argument('--memory', '-mem', type=str, dest='memory',
                        help='Amount of memory to reserve on ErisOne')
    parser.add_argument('--n-cpus', '-cpus', type=str, dest='cpus',
                        help='Number of cpus to reserve on ErisOne')

    args = parser.parse_args()

    # Make the arguments
    jobname = args.rename_study

    lsfdir = args.lsf_basepath

    script_path = os.path.join(lsfdir, 'scripts')
    stdout_loc = os.path.abspath(os.path.join(lsfdir, 'stdout'))
    stderr_loc = os.path.abspath(os.path.join(lsfdir, 'stderr'))
    os.makedirs(script_path, exist_ok=True)
    os.makedirs(stdout_loc, exist_ok=True)
    os.makedirs(stderr_loc, exist_ok=True)
    stdout_loc = os.path.join(stdout_loc, jobname + '.out')
    stderr_loc = os.path.join(stderr_loc, jobname + '.err')

    os.makedirs(lsfdir, exist_ok=True)
    lsfname = os.path.join(script_path, jobname + '.lsf')

    f = open(lsfname, 'w')
    f.write(lsfstr.format(
        jobname=jobname, stdout_loc=stdout_loc, stderr_loc=stderr_loc,
        environment_name=args.environment_name,
        code_basepath=args.code_basepath, queue=args.queue, cpus=args.cpus,
        mem=args.memory, dset_fileloc=args.dataset,
        negbin_run=args.negbin, seed=args.seed, burnin=args.burnin,
        n_samples=args.n_samples, checkpoint=args.checkpoint,
        rename_study=args.rename_study, basepath=args.basepath, a0_level=args.a0_level,
        a1_level=args.a1_level, qpcr_level=args.qpcr_level))
    f.close()
    command = 'bsub < {}'.format(lsfname)
    print(command)
    print("Successfuly got to almost end of python_lsf_syn")
    os.system(command)




#
# # Run the metrics - for later implementation
# # -------------
# mdsine2 metrics\
#     --negbin {negbin_run} \
#     --seed {seed} \
#     --a0-level {a0_level} \
#     --a1-level {a1_level} \
#     --qpcr-level {qpcr_level} \
#     --burnin {burnin} \
#     --n-samples {n_samples} \
#     --checkpoint {checkpoint} \