# MDSINE2: Microbial Dynamical Systems Inference Engine 2

****************************************High level description of the package

## Installation
These instructions install MDSINE2 and download the MDSINE2_Paper git repo

```bash
conda create -n mdsine2 -c conda-forge python=3.7.3 jupyterlab
conda activate mdsine2
python -m ipykernel install --user --name mdsine2 --display-name "mdsine2"
git clone https://github.com/gerberlab/MDSINE2
pip install MDSINE2/.
git clone https://github.com/gerberlab/MDSINE2_Paper
cd MDSINE2_Paper/local_tutorial
jupyter notebook
```

## Tutorials
For tutorials on running MDSINE2, post-processing, and how to use the MDSINE2 software, see `tutorials`.

outline
tutorial 1 data processing
  * List of files needed as input for this and where they are
    * ASV abundance table: asv_abund.tsv
    * Taxonomy of xyz: taxa.tsv
    * etc
  * Step through the scripts executing them, for one of the scripts 'open the hood' to show them what the command looks like and execute it not from the script but in the notebook like one normally wood
  * after all of the scripts have been run give a list of what has been made
  * look at what has been made somehow
  * discuss any pickles that have been made
  * do some head commands or other plotting
  
tutorial 2 run the model
  * List of files needed as input for this and where they are
    * ...
    * ..
    * ...
  * discuss the basic structure of the input data looking at heads
  * comment out the command to run the full model, and instead have a command for running on a simplified system
  * look at output
  * discuss output
  * we need a link to have them download the real output if they want (dropbox link i am thinking? or zonodo)
  
tutorial 3 as an example we can run with the data they created, not sure how feasible it is to run the real data for some tasks that may be large and cumbersome 
  *
  *

## Quick start
#### Running MDSINE2 with Gibson dataset
The raw data of the Gibson dataset is in the folder `datasets/gibson`. To run the MDSINE2 model, use the scripts in the the folder `gibson_dataset`. 

#### Running MDSINE2 with your own dataset
*****************************************************Describe the required tables

1) Parse the tables into a `Study` object
   First we need to parse in the tables of raw data into an MDSINE2 `Study` object
    ```bash
    python step-1_parse_data.py \
        --name name-of-dataset \
        --taxonomy path/to/taxonomy-table.tsv \
        --metadata path/to/metadata-table.tsv \
        --reads path/to/reads-table.tsv \
        --qpcr path/to/qpcr-table.tsv \
        --outfile output/study.pkl
    ```
2) (Optional) Filter the data
    Filter out taxas that don't have enough information
    ```bash
    python step_2_filtering.py \
        --dataset output/study.pkl \
        --outfile output/study_filtered.pkl \
        --dtype DTYPE \
        --threshold THRESHOLD \
        --min-num-consecutive MIN_NUM_CONSECUTIVE \
        --min-num-subjects MIN_NUM_SUBJECTS \
        --colonization-time COLONIZATION_TIME
    ```

3) Learn parameters of MDSINE2 model
   Run the inference of MDSINE2
   ```bash
   python step_5_infer_mdsine2.py \
       --input output/study_filtered.pkl \
       --negbin A0 A1 \
       --seed SEED \
       --burnin BURNIN \
       --n-samples N_SAMPLES \
       --checkpoint CHECKPOINT \
       --basepath output \
       --multiprocessing 0
   ```

4) Visualize the MDSINE2 parameters
   Visualize the parameters
   ```bash
   python step_6_visualize_mdsine2.py \
       --chain output/name-of-dataset/mcmc.pkl \
       --output-basepath output/name-of-dataset/posterior \
       --section posterior
    ```



