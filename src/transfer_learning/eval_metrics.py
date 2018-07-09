import numpy as np
import sklearn.metrics as skm


def auc(y_true, y_pred, round=True):
    """Area under the ROC curve
    """
    if round:
        y_true = y_true.round()
    if len(y_true) == 0 or len(np.unique(y_true)) < 2:
        return np.nan
    return skm.roc_auc_score(y_true, y_pred)


def auprc(y_true, y_pred):
    """Area under the precision-recall curve
    """
    precision, recall, _ = skm.precision_recall_curve(y_true, y_pred)
    return skm.auc(recall, precision)

def accuracy(y_true, y_pred, round=True):
    """Classification accuracy
    """
    if round:
        y_true = np.round(y_true)
        y_pred = np.round(y_pred)
    return skm.accuracy_score(y_true, y_pred)
