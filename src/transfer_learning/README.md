## Reproducing the results

1. Make sure you have run the `snakemake` file from `src/splicing` to download the annotation GTF and FASTA files (see also `src/splicing/download_annotation.smk`)
1. Install the conda environment: 
  - `kipoi env create ../../models/Divergent421 -n kipoi-divergent`
1. Activate the package and install the remaining packages:
  - `source activate kipoi-divergent`
  - `pip install -e ../../`
  - `pip install snakemake concise`
1. Run `snakemake train`
1. Run `snakemake evaluate`
1. Evaluate all cells in `plot.ipynb`


## File description

- `tlearn.py` - script to perform transfer-learning given a Kipoi model and a dataloader
- `Snakefile` - Snakemake file for transfer-learning model training and evaluation
- `plot.ipynb` - Jupyter notebook plotting the results
- `eval_validation.py` - script to evaluate a trained model
- `eval_metrics.py` - required evaluation metrics

## Provided data

- `data/raw/tlearn/intervals_files_complete.tsv.gz` - intervals and DNA accessibility labels for 431 different cell types/tissues
- `data/raw/tlearn/metadata/all_tasks.txt` - columns-names for the labels (ENCODE ID's)
- `data/raw/tlearn/metadata/eval_tasks.txt` - columns for which to evaluate the model (ENCODE ID's)
- `data/raw/tlearn/metadata/anno.csv` - mapping between the ENCODE ID and the Cell_Type for the evaluated tasks
- `data/processed/tlearn/models/random/{split}/{encode_id}/tfdragonn.log` - gathered test and validation logs using tf-dragonn for randomly initialied model
