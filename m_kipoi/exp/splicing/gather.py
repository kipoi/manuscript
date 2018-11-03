import os
from tqdm import tqdm
from collections import OrderedDict
from glob import glob
import pandas as pd
import numpy as np
from kipoi_veff.parsers import KipoiVCFParser


def refmt_col(col, model_name, col_types):
    for ct in col_types:
        if ct in col:
            col = model_name + ct.lower()
            break
    return col


def average_labranchor(df, model_name, col_types):
    import numpy as np
    # choose the maximum diff
    diff_cols = df.columns.values[df.columns.astype(str).str.contains("DIFF")]
    model_outputs = [int(el.split("_")[-1]) for el in diff_cols]
    model_outputs_order = np.argsort(model_outputs)
    # select the model output tha gives the maximum absolute difference
    max_col_id = df[diff_cols[model_outputs_order]].abs().values.argmax(axis=1)
    #
    # just to be sure it will work:
    assert np.all(df[diff_cols[model_outputs_order]].abs().values[np.arange(len(max_col_id)), max_col_id] == df[diff_cols].abs().max(axis=1).values)
    #
    averaged = {}
    usable_columns = df.columns.tolist()
    for ct in col_types:
        col_sel = [col for col in usable_columns if ct in col]
        usable_columns = [col for col in usable_columns if col not in col_sel]
        if len(col_sel) == 0:
            continue
        # average
        model_outputs = [int(el.split("_")[-1]) for el in col_sel]
        model_outputs_order = np.argsort(model_outputs)
        # use the column selection from before
        keep_vals = df[np.array(col_sel)[model_outputs_order]].values[np.arange(len(max_col_id)), max_col_id]
        averaged[model_name + ct.lower()] = keep_vals
    #
    return pd.DataFrame(averaged, index=df.index)


def deduplicate_vars(df):
    diff_cols = df.columns.values[df.columns.str.contains("diff")]
    assert len(diff_cols) == 1
    return df.groupby(df.index).apply(lambda x: x.iloc[np.argmax(x[diff_cols[0]].values), :])


def get_df(vcf_file, model_name):
    df = pd.DataFrame(list(KipoiVCFParser(vcf_file)))
    df.index = df["variant_id"]
    obsolete_variant_columns = ["variant_chr", "variant_pos", "variant_ref", "variant_alt", "variant_id"]
    df = df[[col for col in df.columns if col not in obsolete_variant_columns]]
    df = df[[col for col in df.columns if "rID" not in col]]
    col_types = ["_LOGIT_REF", "_LOGIT_ALT", "_REF", "_ALT", "_DIFF", "_LOGIT"]
    if model_name == "labranchor":
        df = average_labranchor(df, model_name, col_types)
    else:
        df.columns = [refmt_col(col, model_name, col_types) for col in df.columns]
    # clump variants together
    df = deduplicate_vars(df)
    return df


def gather_vcfs(models, base_path, ncores=16):
    """
    Args:
        models: list of model names
        base_path: base path of the directory for storing vcfs: {base_path}/{model}.vcf
        ncores: number of cores used to read the data in paralell
    """
    vcf_fnames = [(m, os.path.join(base_path, "{}.vcf".format(m))) for m in models]

    # all filenames exist
    for m, fname in vcf_fnames:
        assert os.path.exists(fname)

    dfs = {}
    from joblib import Parallel, delayed
    import threading
    threading.current_thread().name = 'MainThread'

    dfs = Parallel(n_jobs=ncores)(delayed(get_df)(vcf_file, model_name) for model_name, vcf_file in vcf_fnames)

    merged_dfs = pd.concat(dfs, axis=1)
    for m in models:
        merged_dfs[m + "_isna"] = merged_dfs[m + "_diff"].isnull()

    # now remove variants for which there are no splicing model predictions:
    merged_dfs_filtered = merged_dfs.loc[merged_dfs[[m + "_isna" for m in models]].sum(axis=1) != len(models), :]
    return merged_dfs_filtered.reset_index().rename(columns={"index": "variant_id"})
