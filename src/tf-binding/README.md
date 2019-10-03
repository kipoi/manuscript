## Reproducing the results

1. Make sure you have run the `snakemake` file from `src/splicing` to download the annotation GTF and FASTA files (see also `src/splicing/download_annotation.smk`)
1. Activate the conda environment for this repository (see [../../README.md](../../README.md) for more information)
  - `source activate kipoi-manuscript`
1. Checkout the additional interval files: `cd data/raw/ && git clone git@github.com:mbeer3/tfbinding.git beer-tfbinding` 
1. Run the whole pipeline (working directory has to be in `src/tfbinding`): `snakemake -p --resources gpu=1 --config gpu=0 -j 32`
  - this will use 32 cores
  - final plots will be located at: `data/processed/tfbinding/eval_<dataset>/plots/all_models.chr8.pdf`
	- `dataset` will be `kipoi`, `DREAM`, `beer-300bp`, `beer-1kb`
  - you can change the GPU ID by changing `--config gpu=<GPU id>`

## File description

- `execution_time.py` - script to measure the execution time of a model
- `Snakefile` - Snakemake file running the entire pipeline

## Provided data

- in folder:`data/raw/tfbinding/eval/tf-DREAM`
  - `DNASE.<cell_type>.relaxed.narrowPeak.gz` - Set of DNASE peaks from the tf-DREAM challenge
  - `chr8_wide_bin101_flank0_stride101.<TF>.<cell_type>.intervals_file.tsv.gz` - bed3 file with an additional column denoting 1-overlaps a ChIP-seq peak, 0=doesn't overlap a ChIP-seq peak
