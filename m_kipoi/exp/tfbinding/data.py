import kipoi
import os
import sys
import pandas as pd
from m_kipoi.exp.tfbinding.config import SINGLE_TASK_MODELS, get_dl_kwargs, TF2CT
from kipoi.readers import HDF5Reader
from concise.eval_metrics import auprc, auc, accuracy
from collections import OrderedDict
from pybedtools import BedTool
import numpy as np
from tqdm import tqdm
from m_kipoi.metrics import classification_metrics, MetricsTupleList, BootstrapMetric
from m_kipoi.config import get_data_dir

ddir = get_data_dir()
root_dir = os.path.join(ddir, '../')
eval_dir = os.path.join(ddir, 'processed/tfbinding/eval/preds')


def get_eval_predictions(tf, model, filter_dnase=False):
    """Get the predictions"""
    with HDF5Reader(os.path.join(eval_dir, tf, model + ".h5")) as r:
        y_pred = r.f['/preds'][:]
    
    labels_bed_file = os.path.join(root_dir, get_dl_kwargs(tf)['intervals_file'])
    df_unfiltered = pd.read_csv(labels_bed_file, sep="\t", header=None)
    df_unfiltered.columns = ['chr', 'start', 'end', 'y_true']
    if filter_dnase:
        # Filter the DNase peaks based on the overlaps
        dnase_peaks = '/mnt/data/TF_binding/DREAM_challenge/public_data/DNASE/peaks/naive_overlap/DNASE.{ctype}.relaxed.narrowPeak.gz'.format(ctype=TF2CT[tf])
        filtered_bed = BedTool(labels_bed_file).intersect(BedTool(dnase_peaks), u=True, wa=True, f=.5)
        df_filtered = pd.read_csv(filtered_bed.fn, sep="\t", header=None)
        df_filtered.columns = ['chr', 'start', 'end', 'y_true']
        df_filtered['filtered'] = True
        keep = df_unfiltered.merge(df_filtered, how='left', on=list(df_unfiltered.columns)).filtered == True
        return df_unfiltered.y_true.values[keep], y_pred[keep]
    else:
        return df_unfiltered.y_true.values, y_pred[:]
    
    
def get_DeepSEA_idx(tf, cell_type):
    """Get the right DeepSEA task index for a certain tf-cell_type"""
    l = [(i, x) for i,x in enumerate(kipoi.get_model_descr("DeepSEA/predict").schema.targets.column_labels) 
         if x.lower().startswith((cell_type + "_" + tf).lower())]
    if len(l) > 1:
        if tf == "JUND":
            return l[1][0]
        print("Multiple entries found {}, {}: {}. Taking the first one".format(tf, cell_type, l))
    if len(l) == 0:
        raise ValueError("No entry found for for {}, {}".format(tf, cell_type))
    return l[0][0]