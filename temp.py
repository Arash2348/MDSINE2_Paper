import mdsine2 as md2
from mdsine2.names import STRNAMES
import pandas as pd
import logging
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

md2.LoggingConfig(level=logging.DEBUG)


##################################################

dset = md2.dataset.load_gibson(dset='uc')

for pert in dset.perturbations:
        print(pert)

sys.exit()
############################################################
import random
import scipy


md2.seed(0)
print(np.random.randint(100, size=5))
print(random.randint(10, 20))
print(scipy.stats.norm.rvs(0,1))

print(md2.random.misc.fast_sample_normal(0, 1))



md2.seed(0)
print(np.random.randint(100, size=5))
print(random.randint(10, 20))
print(scipy.stats.norm.rvs(0,1))

print(md2.random.misc.fast_sample_normal(0, 1))



sys.exit()


# Seeeeeeeed
healthy = md2.Study.load('processed_data/gibson_healthy_agg_taxa_filtered.pkl')
to_delete = []
for taxa in healthy.taxas:
    if taxa.idx > 10:
        to_delete.append(taxa.name)
healthy.pop_taxas(to_delete)

params1 = md2.config.MDSINE2ModelConfig(
        basepath='tmp/params1', seed=100, 
        burnin=10, n_samples=20, negbin_a1=0.0025, 
        negbin_a0=0.025, checkpoint=10)
params1.INITIALIZATION_KWARGS[STRNAMES.CLUSTERING]['value_option'] = 'no-clusters'
params1.LEARN[STRNAMES.CLUSTERING] = False
params1.LEARN[STRNAMES.CONCENTRATION] = True
mcmc1 = md2.initialize_graph(params=params1, graph_name=healthy.name, subjset=healthy)

params2 = md2.config.MDSINE2ModelConfig(
        basepath='tmp/tmp/tmp/params2', seed=100, 
        burnin=10, n_samples=20, negbin_a1=0.0025, 
        negbin_a0=0.025, checkpoint=10)
params2.INITIALIZATION_KWARGS[STRNAMES.CLUSTERING]['value_option'] = 'no-clusters'
params2.LEARN[STRNAMES.CLUSTERING] = False
params2.LEARN[STRNAMES.CONCENTRATION] = True
mcmc2 = md2.initialize_graph(params=params2, graph_name=healthy.name, subjset=healthy)

mcmc1 = md2.run_graph(mcmc1, crash_if_error=True)
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n==============================================================')
mcmc2 = md2.run_graph(mcmc2, crash_if_error=True)


# ele1 = mcmc1.graph[STRNAMES.FILTERING].x.value
# ele2 = mcmc2.graph[STRNAMES.FILTERING].x.value
# for idx in range(len(ele1)):
#     e1 = ele1[idx].value
#     e2 = ele2[idx].value
#     print(e1-e2)
ele1 = mcmc1.graph[STRNAMES.GROWTH_VALUE].get_trace_from_disk(section='entire')[:,0]
ele2 = mcmc2.graph[STRNAMES.GROWTH_VALUE].get_trace_from_disk(section='entire')[:,0]
for i in range(len(ele1)):
    print('{}: {}'.format(i, ele1[i]-ele2[i]))