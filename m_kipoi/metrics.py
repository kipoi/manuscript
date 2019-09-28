import pandas as pd
import numpy as np
from collections import OrderedDict
from concise.eval_metrics import _mask_value_nan, auprc, auc, accuracy

# Metric helpers


class BootstrapMetric:
    def __init__(self, metric, n):
        """
        Args:
          metric: a function accepting (y_true and y_pred) and
             returning the evaluation result
          n: number of bootstrap samples to draw
        """
        self.metric = metric
        self.n = n

    def __call__(self, y_true, y_pred):
        outl = []
        for i in range(self.n):
            bsamples = (
                pd.Series(np.arange(len(y_true))).sample(frac=1, replace=True).values
            )
            outl.append(self.metric(y_true[bsamples], y_pred[bsamples]))
        return outl


class MetricsList:
    """Wraps a list of metrics into a single metric returning a list"""

    def __init__(self, metrics):
        self.metrics = metrics

    def __call__(self, y_true, y_pred):
        return [metric(y_true, y_pred) for metric in self.metrics]


class MetricsDict:
    """Wraps a dictionary of metrics into a single metric returning a dictionary"""

    def __init__(self, metrics):
        self.metrics = metrics

    def __call__(self, y_true, y_pred):
        return {k: metric(y_true, y_pred) for k, metric in self.metrics.items()}


class MetricsTupleList:
    """Wraps a dictionary of metrics into a single metric returning a dictionary"""

    def __init__(self, metrics):
        self.metrics = metrics

    def __call__(self, y_true, y_pred):
        return [(k, metric(y_true, y_pred)) for k, metric in self.metrics]


class MetricsOrderedDict:
    """Wraps a OrderedDict/tuple list of metrics into a single metric 
    returning an OrderedDict
    """

    def __init__(self, metrics):
        self.metrics = metrics

    def __call__(self, y_true, y_pred):
        return OrderedDict([(k, metric(y_true, y_pred)) for k, metric in self.metrics])


# -----------------------------

def auprc_PRROC(y_true, y_pred):
    """Get the auprc_PRROC evaluation metric
    """
    import rpy2.robjects as robjects
    robjects.r('library("PRROC")')
    fn = robjects.r['pr.curve']

    # remove -1 classes
    y_true, y_pred = _mask_value_nan(y_true, y_pred)
    class1p = robjects.FloatVector(list(y_pred[y_true == 1]))
    class0p = robjects.FloatVector(list(y_pred[y_true == 0]))
    return fn(class1p, class0p).rx2("auc.davis.goadrich")[0]


def n_positive(y_true, y_pred):
    return y_true.sum()


def n_negative(y_true, y_pred):
    return (1 - y_true).sum()


def frac_positive(y_true, y_pred):
    return y_true.mean()


classification_metrics = [
    ("auPR", auprc_PRROC),
    ("auPR_scikit", auprc),
    ("auROC", auc),
    ("accuracy", accuracy),
    ("n_positive", n_positive),
    ("n_negative", n_negative),
    ("frac_positive", frac_positive),
]
classification_metric = MetricsOrderedDict(classification_metrics)
