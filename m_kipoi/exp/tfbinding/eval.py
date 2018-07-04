from collections import OrderedDict
from m_kipoi.exp.tfbinding.data import get_DeepSEA_idx, get_eval_predictions
from m_kipoi.exp.tfbinding.config import TF2CT
from m_kipoi.metrics import MetricsTupleList, BootstrapMetric
import sys


def eval_model(tf, model, metrics, n_bootstrap=None, filter_dnase=False):
    exp_dict = [("tf", tf), 
                ("model", model),
                ("filter_dnase", filter_dnase)]
    try:
        y_true, y_pred = get_eval_predictions(tf, model, filter_dnase)
        if model == "DeepSEA":
            y_pred = y_pred[:, get_DeepSEA_idx(tf, TF2CT[tf])]
    except:
        print("Exception occured")
        print(sys.exc_info()[0])
        if n_bootstrap is None:
            return OrderedDict(exp_dict)
        else:
            return [OrderedDict(exp_dict)]
    if n_bootstrap is None:
        # Filter by known regions
        return OrderedDict(exp_dict + MetricsTupleList(metrics)(y_true, y_pred))
    else:
        return [OrderedDict(exp_dict + x) for x in BootstrapMetric(MetricsTupleList(metrics), n=n_bootstrap)(y_true, y_pred)]