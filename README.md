# manuscript_code

Code accompanying the Kipoi manuscript


## Installation

1. Install miniconda or anaconda. 
1. Install git-lfs: `conda install -c conda-forge git-lfs && git lfs install`
1. Clone this repository: `git clone https://github.com/kipoi/manuscript.git && cd manuscript`
1. Run: `git lfs pull '-I data/**''` 
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
