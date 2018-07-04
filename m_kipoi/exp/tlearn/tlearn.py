"""
Useful functions for the transfer-learning case-study
"""
import json
import pandas as pd
import numpy as np
from m_kipoi.exp.tlearn.tfdragonn import parse_log
import os
from m_kipoi.config import get_data_dir
import m_kipoi


def get_exp():
    """Get a dataframe with information about the executed experiments
    """
    dfe = pd.read_csv(os.path.join(get_data_dir(), "raw/tlearn/experiments.tsv"), sep="\t")
    dfe.columns = ['Model', 'ENCODE_ID', 'Cell_Type', 'Log_Path', 'Eval_set',
                   'val_auPRC_epoch1', 'val_auPRC_epoch5', 'val_auPRC_epoch10',
                   'auPRC_tsv', 'auROC_tsv', 'n_epoch', 'Training_Time']
    dfe = dfe[dfe.Model.notnull()]

    # Valid
    df_valid = pd.concat([parse_log("{}/tfdragonn-train".format(dfe.Log_Path[i])) for i in range(len(dfe))]).reset_index()
    df_valid['Log_Path'] = df_valid['path'].map(lambda x: os.path.dirname(x))
    df_valid = df_valid.merge(dfe, on="Log_Path")

    # Test
    df_test = pd.concat([parse_log("{}/tfdragonn-test".format(dfe.Log_Path[i])) for i in range(len(dfe))]).reset_index()
    df_test['Log_Path'] = df_test['path'].map(lambda x: os.path.dirname(x))
    df_test = df_test.merge(dfe, on="Log_Path")
    return df_valid, df_test


def get_metadata():
    """Get metadata on all the tasks
    """
    ddir = get_data_dir()
    conf_json = json.load(open(os.path.join(ddir, "raw/tlearn/raw_intervals_config_file_complete.json")))

    df = pd.DataFrame({"task_name": conf_json['task_names'],
                       "file_path": pd.Series(conf_json['task_names']).map(conf_json['Human']['feature_beds'])})
    df['folder_name'] = df.file_path.map(os.path.basename).str.replace('_rep1-pr.IDR0.1.filt.narrowPeak.gz', '')
    dfm = pd.read_csv(os.path.join(ddir, "raw/tlearn/dnase_metadata_2016-12-05.tsv"), sep="\t")
    df = df.merge(dfm, on="folder_name")
    assert list(df.task_name) == conf_json['task_names']
    return df


def get_all_task_names():
    ddir = get_data_dir()
    with open(os.path.join(ddir, "raw/tlearn/raw_intervals_config_file_complete.json")) as f:
        return json.load(f)['task_names']


def get_multitask_names():
    ddir = get_data_dir()
    with open(os.path.join(ddir, "raw/tlearn/intervalspecfile_holdout_10_nochr1chr8chr9chr21.json")) as f:
        return json.load(f)['task_names']


def get_heldout_names():
    all_names = get_all_task_names()
    multi_task = get_multitask_names()
    return [x for x in all_names if x not in multi_task]


def get_evaluated_task_names():
    dfv, dft = get_exp()
    return dft.ENCODE_ID.unique().tolist()


def distance_summary(metrics=['jaccard', 'cosine']):
    """Get the distance summary for all the used cell-types"""
    from scipy.spatial.distance import squareform
    from scipy.stats import rankdata
    from collections import OrderedDict
    ddir = get_data_dir()

    mlist = []
    for metric in metrics:
        d = np.loadtxt(os.path.join(ddir, "processed/tlearn/dist/{metric}.txt".format(metric=metric)))
        d = squareform(d)
        mlist.append((metric, d))

    # Get the indicies where everything was evaluated
    tnames = pd.Series(get_all_task_names())
    is_evaluated = tnames.isin(get_evaluated_task_names())
    il = np.where(is_evaluated)[0]
    out = []
    for mname, m in mlist:
        for i in il:
            d = m[i]
            # Remove self
            d = d[np.arange(len(d)) != i]
            out.append(OrderedDict([
                ("i", i),
                ("ENCODE_ID", tnames[i]),
                ("metric", mname),
                ("dist_avg", d.mean()),
                ("dist_avg_top_10%", d[rankdata(d) < (len(d) * 0.1)].mean()),
                ("dist_nearest", d.min()),
                ("dist_furthest", d.max()),
            ]))
    dfd = pd.DataFrame(out)
    return dfd


def get_clusters():
    """Get clusters of the data"""
    ddir = get_data_dir()
    tnames = pd.Series(get_all_task_names())
    clusters = np.loadtxt(os.path.join(ddir, "raw/tlearn/clustering/data_clusters.csv")).astype(int)
    dfc = pd.DataFrame({"ENCODE_ID": tnames, "cluster": clusters})
    dfc['cluster_size'] = dfc.groupby("cluster").transform(len)
    return dfc
