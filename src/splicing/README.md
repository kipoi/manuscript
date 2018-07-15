## Reproducing the figure

1. Make sure you have installed all the required dependencies in your current conda environment (see [README](../../README.md)).
1. Make sure you have pulled all the git-lfs files (e.g. `zcat data/processed/splicing/clinvar/20180429.filtered.vcf.gz | head ` should show a vcf file header)
1. Download SPIDEX from: http://www.openbioinformatics.org/annovar/spidex_download_form.php and save it to:
  - `data/raw/splicing/spidex/hg19_spidex.txt.gz`
1. Run `snakemake`
1. Run `train-eval-KipoiSplice4.ipynb` in Jupyter-notebook


## File description

- `train-eval-KipoiSplice4.ipynb` - Jupyter notebook training KipoiSplice4 and plotting the results
- `save_model.ipynb` - Jupyter notebook to save the files to Kipoi
- `Snakefile` - global snakemake file importing the following sub-files
  - `download_annotation.smk` - rules for downloading the required GTF and FASTA genome annotation files
  - `clinvar.smk` - rules for preparing the clinvar data
  - `dbscSNV.smk` - rules for preparing the dbsvSNV data
  - `kipoi.smk` - generic rule for making variant-effect predictions
- `generate_regions.R` - R script generating splice donor and acceptor sites in a bed format
- `functions.R` - functions required by `generate_regions.R`

## Provided files

- `data/processed/splicing/clinvar/annotated_vcf/20180429.filtered/VEP.txt.gz`

## Notes

ClinVar variants were annotated using VEP through the web-interface invoking the following command:

```bash
./vep --af --af_1kg --af_esp --af_gnomad --appris --biotype --check_existing --distance 5000 --plugin LoFtool,[path_to]/ensweb-data[path_to]/LoFtool_scores.txt --plugin MaxEntScan,[path_to]/ensweb-data[path_to]/maxentscan --plugin dbscSNV,[path_to]/ensweb-data[path_to]/dbscSNV1.1_GRCh37.txt.gz --plugin dbNSFP,[path_to]/ensweb-data[path_to]/dbNSFP2.9.2.txt.gz,fold-degenerate,Ancestral_allele,LRT_score,LRT_converted_rankscore,LRT_pred,MutationTaster_score,MutationTaster_converted_rankscore,MutationTaster_pred,MutationAssessor_score,MutationAssessor_rankscore,MutationAssessor_pred,FATHMM_score,FATHMM_rankscore,FATHMM_pred,MetaSVM_score,MetaSVM_rankscore,MetaSVM_pred,MetaLR_score,MetaLR_rankscore,MetaLR_pred,Reliability_index,VEST3_score,VEST3_rankscore,PROVEAN_score,PROVEAN_converted_rankscore,PROVEAN_pred,M-CAP_score,M-CAP_rankscore,M-CAP_pred,Eigen_coding_or_noncoding,Eigen-raw,Eigen-phred,Eigen-PC-raw,Eigen-PC-phred,Eigen-PC-raw_rankscore,CADD_raw,CADD_raw_rankscore,CADD_phred,GERP++_NR,GERP++_RS,GERP++_RS_rankscore,phyloP46way_primate,phyloP46way_primate_rankscore,phyloP46way_placental,phyloP46way_placental_rankscore,phyloP100way_vertebrate,phyloP100way_vertebrate_rankscore,phastCons46way_primate,phastCons46way_primate_rankscore,phastCons46way_placental,phastCons46way_placental_rankscore,phastCons100way_vertebrate,phastCons100way_vertebrate_rankscore,SiPhy_29way_pi,SiPhy_29way_logOdds,SiPhy_29way_logOdds_rankscore,LRT_Omega,UniSNP_ids,1000Gp1_AC,1000Gp1_AF,1000Gp1_AFR_AC,1000Gp1_AFR_AF,1000Gp1_EUR_AC,1000Gp1_EUR_AF,1000Gp1_AMR_AC,1000Gp1_AMR_AF,1000Gp1_ASN_AC,1000Gp1_ASN_AF,ESP6500_AA_AF,ESP6500_EA_AF,ARIC5606_AA_AC,ARIC5606_AA_AF,ARIC5606_EA_AC,ARIC5606_EA_AF,ExAC_AC,ExAC_AF,ExAC_Adj_AC,ExAC_Adj_AF,ExAC_AFR_AC,ExAC_AFR_AF,ExAC_AMR_AC,ExAC_AMR_AF,ExAC_EAS_AC,ExAC_EAS_AF,ExAC_FIN_AC,ExAC_FIN_AF,ExAC_NFE_AC,ExAC_NFE_AF,ExAC_SAS_AC,ExAC_SAS_AF,clinvar_rs,clinvar_clnsig,clinvar_trait,clinvar_golden_stars,COSMIC_ID,COSMIC_CNT --plugin CADD,[path_to]/ensweb-data[path_to]/CADD.tsv.gz,[path_to]/ensweb-data[path_to]/CADD_InDels.tsv.gz --polyphen b --pubmed --regulatory --sift b --species homo_sapiens --symbol --tsl --cache --input_file [input_data]
```

Annotated file can be found here: `data/processed/splicing/clinvar/annotated_vcf/20180429.filtered/VEP.txt.gz`
