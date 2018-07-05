import pandas as pd
import numpy as np
import os
import dask.dataframe as dd
from m_kipoi.config import get_data_dir
from openpyxl import Workbook, load_workbook
DATA = get_data_dir()


def get_clinvar_ext_Xy(clinvar='20180429', keep_variants="^Pathogenic$|^Benign$"):
    """Load the clinvar data

    Args:
      clinvar: clinvar version (publication date)
      keep_variants: regex of variants to keep
    """
    def variant_id(chr, pos, ref, alt):
        return chr.astype(str) + ":" + pos.astype(str) + ":" + ref + ":['" + alt + "']"

    ddir = get_data_dir()
    df = pd.read_csv(f"{ddir}/processed/splicing/clinvar/annotated_vcf/{clinvar}.filtered/modeling_df.tsv", sep='\t')
    # Keep only Kipoi annotations
    df = df.iloc[:, ~df.columns.str.startswith("other_")]

    # Append clinical significance
    from kipoi.postprocessing.variant_effects import KipoiVCFParser
    vcf_file = f"{ddir}/processed/splicing/clinvar/{clinvar}.filtered.vcf.gz"
    dfc = pd.DataFrame(list(KipoiVCFParser(vcf_file)))
    dfc['variant_id_old'] = dfc['variant_id']
    dfc['variant_id'] = variant_id(dfc.variant_chr, dfc.variant_pos, dfc.variant_ref, dfc.variant_alt)
    dfc['ClinicalSignificance'] = dfc['other_CLNSIG']
    # import ipdb
    # ipdb.set_trace()
    df = pd.merge(df, dfc[['variant_id', 'ClinicalSignificance']], on='variant_id', validate="many_to_one").drop_duplicates()

    # add the differences
    df["pathogenic"] = df.ClinicalSignificance == "Pathogenic"

    splicing_models = ["MaxEntScan/3prime", "MaxEntScan/5prime", "HAL", "labranchor"]
    for m in splicing_models:
        df[m + "_diff"] = df[m + "_ref"] - df[m + "_ref"]
        df[m + "_isna"] = df[m + "_ref"].isnull().astype(float)

    only_NA_rows = df[[m + "_diff" for m in splicing_models]].isnull().all(axis=1)

    df = df[~only_NA_rows]
    df = df[~df.ClinicalSignificance.isnull()]
    df = df[df.ClinicalSignificance.str.match(keep_variants)]

    # Append conservation scores and dbscSNV from VEP
    df_vep = pd.read_csv(f"{ddir}/processed/splicing/clinvar/annotated_vcf/{clinvar}.filtered/VEP.txt.gz",
                         sep='\t', na_values='-')
    df_vep = df_vep.join(df_vep.Location.str.split(":|-", expand=True).rename(columns={0: "chr", 1: "start", 2: "end"}))

    df_vep['start'] = df_vep.start.astype(float)
    df_vep['end'] = df_vep.end.astype(float)
    df_vep['variant_id'] = variant_id(df_vep['chr'], df_vep.start.astype(int), df_vep.GIVEN_REF, df_vep.Allele)
    cons_features = ["CADD_raw", "CADD_phred", "phyloP46way_placental", "phyloP46way_primate"]
    splice_features = ['rf_score', 'MaxEntScan_diff']

    # exclude stop_gained variants
    exclude = df_vep[df_vep.Consequence.str.startswith("stop_gained")]['#Uploaded_variation'].unique()
    df_vep["early_stop"] = df_vep['#Uploaded_variation'].isin(exclude)

    df = pd.merge(df,
                  df_vep[["variant_id", "early_stop"] +
                         cons_features +
                         splice_features].drop_duplicates(["variant_id"]),
                  on=["variant_id"], how='left', validate="many_to_one").drop_duplicates()

    # Append spidex
    df_spidex = pd.read_csv(f"{ddir}/raw/splicing/spidex/hg19_spidex.clinvar_{clinvar}.txt", sep='\t')
    df_spidex = df_spidex.drop_duplicates()
    df_spidex['variant_id'] = variant_id(df_spidex["#Chr"].astype(str), df_spidex.Start, df_spidex.Ref, df_spidex.Alt)
    df = pd.merge(df, df_spidex[['variant_id', 'dpsi_max_tissue', 'dpsi_zscore']], on="variant_id", how='left')
    df['dpsi_max_tissue_isna'] = df['dpsi_max_tissue'].isnull()
    df['dpsi_zscore_isna'] = df['dpsi_zscore'].isnull()
    df.loc[df.dpsi_max_tissue.isnull(), "dpsi_max_tissue"] = 0
    df.loc[df.dpsi_zscore.isnull(), "dpsi_zscore"] = 0

    # Append dbscSNV
    dbsc = dd.read_csv(f"{ddir}/raw/splicing/dbscSNV/dbscSNV.chr*", sep='\t', dtype={'chr': 'object'}, na_values=".").compute()
    dbsc['variant_id'] = variant_id(dbsc.chr, dbsc.pos, dbsc.ref, dbsc.alt)
    dbsc = dbsc.rename(columns={'rf_score': 'dbscSNV_rf_score', 'ada_score': 'dbscSNV_ada_score'})
    df = pd.merge(df, dbsc, on='variant_id', how='left')
    df['dbscSNV_rf_score_isna'] = df.dbscSNV_rf_score.isnull()
    df['dbscSNV_ada_score_isna'] = df.dbscSNV_ada_score.isnull()
    df.loc[df.dbscSNV_rf_score.isnull(), 'dbscSNV_rf_score'] = 0
    df.loc[df.dbscSNV_ada_score.isnull(), 'dbscSNV_ada_score'] = 0

    y_clinvar = np.array(df.ClinicalSignificance == "Pathogenic")
    X_clinvar = df.loc[:, df.columns != 'ClinicalSignificance']
    X_clinvar = X_clinvar.iloc[:, ~X_clinvar.columns.str.contains("diff")]

    return X_clinvar, y_clinvar


def get_dbscsnv_data():
    """Loads the dbscsnv data"""
    cache_path = os.path.join(DATA, "raw/splicing/dbscSNV/Supplementary_Table_S2.tsv")
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path, sep="\t")
    wb = load_workbook(os.path.join(DATA, "raw/splicing/dbscSNV/Supplementary_Table_S1-S6.xlsx"))

    it = iter(wb["Table S2"].values)
    _ = next(it)
    header = next(it)

    df = pd.DataFrame(it, columns=header)
    # Cleanup
    df = df.rename(columns={"Splice site": "Splice_site"})
    df['Chr'] = df.Chr.astype(str)
    return df


def get_dbscsnv_Xy():
    """Load the dbscSNV data with additional columns from kipoi models
    """
    ddir = get_data_dir()
    df = pd.read_csv(os.path.join(ddir, "processed/splicing/dbscSNV/modeling_df.tsv"), sep='\t')
    df['Chr'] = df.Chr.astype(str)

    # append spidex
    df_spidex = pd.read_csv(f"{ddir}/raw/splicing/spidex/hg19_spidex.dbscSNV.txt", sep='\t')
    df_spidex['Chr'] = df_spidex["#Chr"].astype(str)
    del df_spidex['#Chr']
    df_spidex = df_spidex.rename(columns={"Start": "Position", "End": "end"})
    df_spidex = df_spidex.drop_duplicates()
    df = pd.merge(df, df_spidex, on=["Chr", "Position", "Ref", "Alt"], how='left', validate='one_to_one')
    df['dpsi_max_tissue_isna'] = df['dpsi_max_tissue'].isnull()
    df['dpsi_zscore_isna'] = df['dpsi_zscore'].isnull()
    df.loc[df.dpsi_max_tissue.isnull(), "dpsi_max_tissue"] = 0
    df.loc[df.dpsi_zscore.isnull(), "dpsi_zscore"] = 0

    # Append dbscSNV
    dbsc = dd.read_csv(f"{ddir}/raw/splicing/dbscSNV/dbscSNV.chr*",
                       sep='\t', dtype={'chr': 'object'}, na_values=".").compute()
    dbsc.rename(columns={"chr": "Chr", "pos": "Position",
                         "ref": "Ref", "alt": "Alt"},
                copy=False, inplace=True)
    df = pd.merge(df, dbsc, on=["Chr", "Position", "Ref", "Alt"], how='left', validate="one_to_one")
    df = df.rename(columns={'rf_score': 'dbscSNV_rf_score', 'ada_score': 'dbscSNV_ada_score'})
    df['dbscSNV_rf_score_isna'] = df.dbscSNV_rf_score.isnull()
    df['dbscSNV_ada_score_isna'] = df.dbscSNV_ada_score.isnull()
    df.loc[df.dbscSNV_rf_score.isnull(), 'dbscSNV_rf_score'] = 0
    df.loc[df.dbscSNV_ada_score.isnull(), 'dbscSNV_ada_score'] = 0

    # TODO - append the conservation scores

    # crete x,y
    y_dbscsnv = np.array(df.Group == "Positive")
    X_dbscsnv = df.iloc[:, df.columns != "Group"]
    return X_dbscsnv, y_dbscsnv
