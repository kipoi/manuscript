- setup the whole evaluation in one snakefile: `experiments/tfbinding/Snakefile`
  - similar to: https://github.com/kipoi/manuscript_code/blob/master/Snakefile#L111-L183

## Snakemake rules

- download evaluation data
- create conda env
- predict
  - simply runs `kipoi predict` for each model
   - make sure `use_linecache` is enabled
   - enable compression of the hdf5 file
- evaluate
  - runs the evaluation for each model and outputs
     -  bootstraped table as a csv file. Metrics:
       - auprc, recall at fdr x, auROC, accuracy, num_positive, num_negative
     - single-lined csv file with only a single evaluation
- plot
  - gathers the multiple csv files and plots the results

## Evaluation files

- see: https://github.com/kipoi/manuscript_code/tree/master/experiments/tfbinding/interval_specs
  - `<TF>.<cell_line>.testing.json`

## Deepsea example

```bash
#!/bin/bash

intervals_file='/srv/scratch/manyu/kipoi/manuscript_code/experiments/tfbinding/interval_files/chr8_wide_bin101_flan\
k0_stride101_slop_l450_r449.CEBPB.HeLa-S3.intervals_file.tsv'
genome_file='/srv/scratch/genomelake_data/hg19.genome.fa'
#echo '{"intervals_file": "'$intervals_file'", "fasta_file": "'$genome_file'"}'
kipoi predict DeepSEA/predict \
  --dataloader='dataloaders/genomelake/ArrayExtractorSeq_Dataset' \
  --dataloader_source=kipoi \
  --dataloader_args='{"intervals_file": "'$intervals_file'", "genome_file": "'$genome_file'","use_linecache":True}' \
  --batch_size=512 \
  -n 16 \
  -o 'predictions/DeepSEA_predict.h5'
```