# manuscript_code

Code accompanying the Kipoi manuscript


## Installation

1. Install miniconda or anaconda. 
1. Install git-lfs: `conda install -c conda-forge git-lfs && git lfs install`
1. Clone this repository: `git clone https://github.com/kipoi/manuscript.git && cd manuscript`
1. Run: `git lfs pull '-I data/**'` 
1. Run: `conda env create -f env.yaml`. This will install a new conda environment `kipoi-manuscript`
1. Activate the environment: `source activate kipoi-manuscript`
1. Install the `m_kipoi` python package for this repository : `pip install -e .`


## Folder organization

- `m_kipoi` - python package (contains python functions/classes common across multiple notebooks)
- `src` - scripts for running the experiments and producing the figures
  - `tf-binding` - Figure 2
  - `transfer_learnining` - Figure 3
  - `mutationmaps` - Figure 4
  - `splicing` - Figure 5
- `data` - data files
- `models/Divergent421` - (optional) Pre-trained DNA accessibility model (Kipoi format)
- `slurm` - (optional) SLURM profile for snakemake <https://github.com/Snakemake-Profiles/slurm>

## Overview by use-cases

- Fig 2 - Making model predictions using a generic command
  - With Snakemake, it's possible to write a generic command
  and make predictions for all the models
    - Each model is executed in a separate conda environment
      - [Installation rule](https://github.com/kipoi/manuscript/blob/master/src/tf-binding/Snakefile#L119-L126)
      - [Prediction rule](https://github.com/kipoi/manuscript/blob/master/src/tf-binding/Snakefile#L130-L155)
      - Function to get the `kipoi` binary given the conda environment name: [get_env_executable](https://github.com/kipoi/manuscript/blob/master/m_kipoi/utils.py#L59-L64)
- Fig 3 - Transfer learning: 
  - Script for performing transfer-learning using a Keras-based model from Kipoi: [tlearn.py](https://github.com/kipoi/manuscript/blob/master/src/transfer_learning/tlearn.py)
  - Pre-computing the activations of the frozen part of the network and then training the model [pre-computed-tlearn.ipynb](https://github.com/kipoi/manuscript/blob/master/src/transfer_learning/pre-computed-tlearn.ipynb)
- Fig 4 - Plugins (variant effect prediction and interpretation)
  - Generic rule for variant effect prediction (CLI) used for building KipoiSplice/4 (relevant for Fig. 4 and Fig. 5):
    - [create_env](https://github.com/kipoi/manuscript/blob/master/src/splicing/kipoi.smk#L8-L14)
	- [annotate_vcf](https://github.com/kipoi/manuscript/blob/master/src/splicing/kipoi.smk#L17-L41)
  - Producing a mutation-map (Figure 4): [src/mutationmaps/plot.ipynb](https://github.com/kipoi/manuscript/blob/master/src/mutationmaps/plot.ipynb)
- Fig 5 - Composite models
  - Tutorial: http://kipoi.org/docs/tutorials/composing_models/
  - Concrete example (KipoiSplice/4): [KipoiSplice/4/dataloader.py](https://github.com/kipoi/models/blob/master/KipoiSplice/4/dataloader.py#L80-L152)
