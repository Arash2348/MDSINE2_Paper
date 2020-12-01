'''Preprocess (aggregate and filter) the Gibson dataset for Healthy cohort, 
Ulcerative Colitis cohort, inoculum, and replicate read datasets.

Author: David Kaplan
Date: 11/17/20
MDSINE2 version: 4.0.2

Methodology
-----------
1) Load the dataset
2) Set the sequences of the Taxas to the aligned sequences used in building the 
   phylogenetic tree, instead of them straight from DADA2 (those are unaligned).
   We set the sequences of the Taxas to be gapless, i.e. we remove all alignment
   positions where any sequence has a gap.
3) Aggregate Taxas with a specified hamming distance
4) Rename aggregated Taxas into OTUs

Parameters
----------
--dataset, -i, -d : str (multiple)
    This is the Gibson dataset that you want to parse. You can load in multiple datasets.
--hamming-distance, -hd : int
    This is the hamming radius to aggregate Taxa sequences. If nothing is provided, 
    then there will be no aggregation.
--rename-prefix, -rp : str
    This is the prefix you are renaming the aggregate Taxas to. If nothing is provided,
    then they will not be renamed.
--sequences, -s : str
    This is the fasta file location of the aligned sequences for each Taxa that was 
    used for placement in the phylogenetic tree. If nothing is provided, then do 
    not replace them.
--outfile, -o : str (multiple)
    This is where you want to save the parsed dataset. Each dataset in `--dataset` must
    have an output.

Reproducability
---------------
To reproduce the paper, run:
Linux/MacOS:
python gibson_1_preprocessing.py \
    --dataset healthy uc replicates \
    --hamming-distance 2 \
    --rename-prefix OTU \
    --sequences gibson_files/preprocessing/gibson_16S_rRNA_v4_seqs_aligned_filtered.fa \
    --outfile gibson_output/datasets/gibson_healthy_agg.pkl gibson_output/datasets/gibson_uc_agg.pkl \
              gibson_output/datasets/gibson_replicate_agg.pkl 
PC:
python gibson_1_preprocessing.py `
    --dataset healthy uc replicates `
    --hamming-distance 2 `
    --rename-prefix OTU `
    --sequences gibson_files/preprocessing/gibson_16S_rRNA_v4_seqs_aligned_filtered.fa `
    --outfile gibson_output/datasets/gibson_healthy_agg.pkl gibson_output/datasets/gibson_uc_agg.pkl `
              gibson_output/datasets/gibson_replicate_agg.pkl 

The file `paper_files/preprocessing/gibson_16S_rRNA_v4_seqs_aligned_filtered.fa` 
was prepared by first aligning the Taxa sequences to the reference sequeunces in the 
phylogenetic tree. Once aligned, Taxas were manually filtered out if they had poor alignment 
within the 16S rRNA v4 region. A fasta file of the Taxas removed as well as their alignments 
can be found in `paper_files/preprocessing/prefiltered_asvs.fa`. 


See Also
--------
mdsine2.visualization.aggregate_taxa_abundances
'''
import argparse
import pandas as pd
from Bio import SeqIO
import numpy as np
import logging
import mdsine2 as md2

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', '-d', '-i', type=str, dest='datasets',
        help='This is the Gibson dataset that you want to parse. You can load in ' \
            'multiple datasets.', nargs='+')
    parser.add_argument('--outfile', '-o', type=str, dest='outfiles',
        help='This is where you want to save the parsed dataset. Each dataset in ' \
            '`--dataset` must have an output.', nargs='+')
    parser.add_argument('--hamming-distance', '-hd', type=int, dest='hamming_distance',
        help='This is the hamming radius to aggregate Taxa sequences. If nothing ' \
            'is provided, then there will be no aggregation.', default=None)
    parser.add_argument('--rename-prefix', '-rp', type=str, dest='rename_prefix',
        help='This is the prefix you are renaming the aggregate taxas to. ' \
            'If nothing is provided, then they will not be renamed', default=None)
    parser.add_argument('--sequences', '-s', type=str, dest='sequences',
        help='This is the fasta file location of the aligned sequences for each Taxa' \
            ' that was used for placement in the phylogenetic tree. If nothing is ' \
            'provided, then do not replace them.', default=None)
    
    args = parser.parse_args()
    md2.config.LoggingConfig(level=logging.INFO)
    if len(args.datasets) != len(args.outfiles):
        raise ValueError('Each dataset ({}) must have an outfile ({})'.format(
            len(args.datasets), len(args.outfiles)))

    for iii, dset in enumerate(args.datasets):
        print('\n\n----------------------------')
        print('On Dataset {}'.format(dset))

        # 1) Load the dataset
        study = md2.dataset.gibson(dset=dset, as_df=False, species_assignment='both')

        # 2) Set the sequences for each Taxa
        #    Remove all taxas that are not contained in that file
        #    Remove the gaps
        if args.sequences is not None:
            print('Replacing sequences with the file {}'.format(args.sequences))
            seqs = SeqIO.to_dict(SeqIO.parse(args.sequences, format='fasta'))
            to_delete = []
            for taxa in study.taxas:
                if taxa.name not in seqs:
                    to_delete.append(taxa.name)
            for name in to_delete:
                print('Deleting {} because it was not in {}'.format(
                    name, args.sequences))
            study.pop_taxas(to_delete)

            M = []
            for taxa in study.taxas:
                seq = list(str(seqs[taxa.name].seq))
                M.append(seq)
            M = np.asarray(M)
            gaps = M == '-'
            n_gaps = np.sum(gaps, axis=0)
            idxs = np.where(n_gaps == 0)[0]
            print('There are {} positions where there are no gaps out of {}. Setting those ' \
                'to the sequences'.format(len(idxs), M.shape[1]))
            M = M[:, idxs]
            for i,taxa in enumerate(study.taxas):
                taxa.sequence = ''.join(M[i])

        # 3) Aggregate with specified hamming distance
        if args.hamming_distance is not None:
            print('Aggregating Taxas with a hamming distance of {}'.format(args.hamming_distance))
            study = md2.aggregate_items(subjset=study, hamming_dist=args.hamming_distance)

            # Get the maximum distance of all the OTUs
            m = -1
            for taxa in study.taxas:
                if md2.isotu(taxa):
                    for aname in taxa.aggregated_taxas:
                        for bname in taxa.aggregated_taxas:
                            if aname == bname:
                                continue
                            aseq = taxa.aggregated_seqs[aname]
                            bseq = taxa.aggregated_seqs[bname]
                            d = md2.diversity.beta.hamming(aseq, bseq)
                            if d > m:
                                m = d
            print('Maximum distance within an OTU: {}'.format(m))
        
        # 4) Rename taxas
        if args.rename_prefix is not None:
            print('Renaming Taxas with prefix {}'.format(args.rename_prefix))
            study.taxas.rename(prefix=args.rename_prefix, zero_based_index=False)

        # 5) remove timepoints in the beginning
        if dset in ['healthy', 'uc']:
            print('removing from dataset')
            for subj in study:
                study.pop_times(times=[0, 0.5, 1], sids='all')


        # Save
        study.save(args.outfiles[iii])
