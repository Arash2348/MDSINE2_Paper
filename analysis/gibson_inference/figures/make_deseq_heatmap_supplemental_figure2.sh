#!/bin/bash


python gibson_inference/figures/deseq_heatmap_ss.py \
    -loc "gibson_inference/figures/supplemental_figure2_files" \
    -abund "high" \
    -txt "abundant_species_phylum" \
    -taxo "phylum" \
    -o "mat_phylum_high_ss" \
    -o_loc "gibson_inference/figures/output_figures"


python gibson_inference/figures/deseq_heatmap_ss.py \
    -loc "gibson_inference/figures/supplemental_figure2_files" \
    -abund "low" \
    -txt "abundant_species_phylum" \
    -taxo "phylum" \
    -o "mat_phylum_low_ss" \
    -o_loc "gibson_inference/figures/output_figures"

python gibson_inference/figures/deseq_heatmap_phylum.py \
    -loc "gibson_inference/figures/supplemental_figure2_files" \
    -abund "high" \
    -txt "abundant_species_phylum" \
    -taxo "phylum" \
    -o "mat_phylum_high" \
    -o_loc "gibson_inference/figures/output_figures"


python gibson_inference/figures/deseq_heatmap_phylum.py \
    -loc "gibson_inference/figures/supplemental_figure2_files" \
    -abund "low" \
    -txt "abundant_species_phylum" \
    -taxo "phylum" \
    -o "mat_phylum_low" \
    -o_loc "gibson_inference/figures/output_figures"
