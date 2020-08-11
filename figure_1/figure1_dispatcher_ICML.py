import numpy as np
import os
import shutil
import argparse


parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument('--n-asvs', '-o', type=int,
    help='Number of ASVs', dest='n_asvs', default=50)
parser.add_argument('--n-data-seeds', '-d', type=int,
    help='Number of data seeds for each noise level', 
    dest='n_data_seeds', default=5)
parser.add_argument('--n-init-seeds', '-i', type=int,
    help='Number of initialization seeds for each data seed', 
    dest='n_init_seeds', default=1)
parser.add_argument('--n-samples', '-ns', type=int,
        help='Total number of Gibbs steps to do',
        dest='n_samples', default=6000)
parser.add_argument('--burnin', '-nb', type=int,
    help='Total number of burnin steps',
    dest='burnin', default=3000)
parser.add_argument('--basepath', '-b', type=str,
    help='Basepath to save the output', default=None,
    dest='basepath')
parser.add_argument('--data-path', '-db', type=str,
    help='Folder to lead the data from', dest='data_path')
parser.add_argument('--n-replicates', '-nr', type=int,
    help='How many replicates of data to run with.', dest='n_replicates',
    default=5, nargs='+')
parser.add_argument('--measurement-noises', '-m', type=float,
    help='What measurement noises to run it at', default=[0.05, 0.1, 0.15],
    dest='measurement_noises', nargs='+')
parser.add_argument('--process-variances', '-p', type=float,
    help='What process varainces to run with', default=[0.05],
    dest='process_variances', nargs='+')
parser.add_argument('--n-cpus', '-nc', type=int, 
    help='Number of CPUs to reserve', dest='n_cpus', default=6)
parser.add_argument('--n-gbs', '-ng', type=int, 
    help='Number og GBs to reserve for the job', dest='n_gbs', default=10000)
parser.add_argument('--n-times', '-nt', type=int,
        help='Number of time points', 
        dest='n_times', default=[30, 45, 60, 75, 90], nargs='+')
parser.add_argument('--clustering-ons', '-co', type=int,
    help='To run with clustering on and off', default=[1,0],
    dest='clustering_on', nargs='+')
args = parser.parse_args()

if type(args.n_replicates) == int:
    args.n_replicates = [args.n_replicates]
measurement_noises = args.measurement_noises
process_variances = args.process_variances
data_seeds = np.arange(0,args.n_data_seeds)
init_seeds = np.arange(0,args.n_init_seeds)
if args.basepath is None:
    basepath = 'figure1_ICML{}/'.format(args.n_asvs)
else:
    basepath = args.basepath

my_str = '''
#!/bin/bash
#BSUB -J {0}
#BSUB -o {1}_output.out
#BSUB -e {1}_error.err

# This is a sample script with specific resource requirements for the
# **bigmemory** queue with 64GB memory requirement and memory
# limit settings, which are both needed for reservations of
# more than 40GB.
# Copy this script and then submit job as follows:
# ---
# cd ~/lsf
# cp templates/bsub/example_8CPU_bigmulti_64GB.lsf .
# bsub < example_bigmulti_8CPU_64GB.lsf
# ---
# Then look in the ~/lsf/output folder for the script log
# that matches the job ID number

# Please make a copy of this script for your own modifications

#BSUB -q big-multi
#BSUB -n {2}
#BSUB -M {3}
#BSUB -R rusage[mem={3}]

# Some important variables to check (Can be removed later)
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

# Add your job command here
# Load module
module load anaconda
source activate dispatcher

cd /data/cctm/darpa_perturbation_mouse_study/perturbation_study/figure_1/
python main_ICML.py -m {4} -p {5} -d {6} -i {7} -b {8} -n {9} -nb {10} -ns {11} -nr {12} -c {13} -nt {14} -db {15} -us {16}
'''
# try:
#     os.mkdir(basepath)
# except OSError:
#     # Remove the directory and then make one
#     shutil.rmtree(basepath)
#     os.mkdir(basepath)
os.makedirs(basepath, exist_ok=True)

# Make dir for lsf files, outputs and error files
lsfdir = basepath + 'lsfs/'
logdir = basepath + 'logs/'
os.makedirs(lsfdir, exist_ok=True)
os.makedirs(logdir, exist_ok=True)

# # Full mesh
# for nr in args.n_replicates:
#     for clustering_on in args.clustering_on:
#         for mn in measurement_noises:
#             for pv in process_variances:
#                 for d in data_seeds:
#                     for i in init_seeds:

#                         # Make name
#                         name = 'n{}_d{}_i{}_ns{}_nb{}_nr{}_m{}_p{}_co{}'.format(
#                             args.n_asvs, d,i,args.n_samples, args.burnin,nr, mn, pv, 
#                             clustering_on)
#                         lsfname = lsfdir + name + '.lsf'
#                         f = open(lsfname, 'w')
#                         f.write(my_str.format(
#                             name, 
#                             logdir + name,
#                             args.n_cpus,
#                             args.n_gbs, 
#                             mn, pv, d, i, basepath,
#                             args.n_asvs, args.burnin, 
#                             args.n_samples, nr, 
#                             clustering_on))
#                         f.close()
#                         os.system('bsub < {}'.format(lsfname))

# Partial meshes
# (N replicates, N timepoints, N data seeds, N init seeds, Measurment noise, process variance, 
#   uniform sampling for timepoints, which type of booxplot is happening)
# If there is an array in one of the parameters (except for the seeds), then we iterate over
# Those keeping the other parameters fixed

meshes = [
    ([5], [65], 10, 1, [0.05, 0.1, 0.2, 0.3, 0.4], [0.05], [1], 0, 0),    
    ([2,3,4,5], [55,65,45], 10, 1, [0.2, 0.3], [0.05], [1], 0, 1), 
    ([4], [25, 35, 45, 55], 10, 1, [0.3, 0.2], [0.05], [1], 1, 2)]

for mesh in meshes:
    n_replicates = mesh[0]
    n_timepoints = mesh[1]
    n_data_seeds = mesh[2]
    n_init_seeds = mesh[3]
    measurement_noises = mesh[4]
    process_variances = mesh[5]
    clustering_ons = mesh[6]
    uniform_sampling = mesh[7]
    boxplot_type = mesh[8]

    for nr in n_replicates:
        for nt in n_timepoints:
            for mn in measurement_noises:
                for pv in process_variances:
                    for d in range(n_data_seeds):
                        for i in range(n_init_seeds):
                            for co in clustering_ons:
                                # Make name
                                if boxplot_type == 0:
                                    # Do measurement 
                                    jobname = 'MC{}m{}'.format(d,mn)
                                elif boxplot_type == 1:
                                    # Do replicates
                                    jobname = 'MC{}r{}'.format(d,nr)
                                else:
                                    # Do number of timepoints
                                    jobname = 'MC{}t{}'.format(d,nt)

                                name = 'n{}_d{}_i{}_ns{}_nb{}_nr{}_m{}_p{}_co{}_nt{}_us{}'.format(
                                    args.n_asvs, d,i, args.n_samples, args.burnin, nr, mn, pv, 
                                    co, nt, uniform_sampling)
                                lsfname = lsfdir + name + '.lsf'
                                f = open(lsfname, 'w')
                                f.write(my_str.format(
                                    jobname, 
                                    logdir + name,
                                    args.n_cpus,
                                    args.n_gbs, 
                                    mn, pv, d, i, basepath,
                                    args.n_asvs, args.burnin, 
                                    args.n_samples, nr, 
                                    co, nt, args.data_path, uniform_sampling))
                                f.close()
                                os.system('bsub < {}'.format(lsfname))




                        
