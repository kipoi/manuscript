# manuscript_code

Research code for the kipoi manuscript


## Installation

1. Install miniconda or anaconda. 
1. Install git-lfs: `conda install -c conda-forge git-lfs && git lfs install`
1. Clone this repository: `git clone https://github.com/kipoi/manuscript.git && cd manuscript`
1. Run: `git lfs pull '-I /'` 
1. Run: `conda env create -f env.yml`. This will install a new conda environment `kipoi-manuscript`
1. Activate the environment: `source activate kipoi-manuscript`
1. Install the `m_kipoi` python package for this repository : `pip install -e .`


## Folder organization

- m_kipoi - main python package folder for the kipoi manuscript (place for hosting functions that will get re-used throughout the analysis
- src - scripts for producing the figures


## TODO

- check if git lfs pull indeed works correctly
