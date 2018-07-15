## Reproducing the results

1. Make sure you have run the `snakemake` file from `src/splicing` to download the annotation GTF and FASTA files (see also `src/splicing/download_annotation.smk`)
1. Activate the conda environment for this repository (see [../../README.md](../../README.md) for more information)
  - `source activate kipoi-manuscript`
1. Run the whole pipeline: `snakemake`
  - final plots will be located at: `data/processed/tfbinding/eval/plots/all_models.chr8.pdf`

## File description

- `execution_time.py` - script to measure the execution time of a model
- `Snakefile` - Snakemake file running the entire pipeline

## Provided data

- in folder:`data/raw/tfbinding/eval/tf-DREAM`
  - `DNASE.<cell_type>.relaxed.narrowPeak.gz` - Set of DNASE peaks from the tf-DREAM challenge
  - `chr8_wide_bin101_flank0_stride101.<TF>.<cell_type>.intervals_file.tsv.gz` - bed3 file with an additional column denoting 1-overlaps a ChIP-seq peak, 0=doesn't overlap a ChIP-seq peak