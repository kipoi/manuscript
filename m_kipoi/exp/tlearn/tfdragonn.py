"""Utils for tfdragonn by @avsecz
"""
from kipoi.utils import read_txt
import re
import numpy as np
import pandas as pd


def parse_log(path):
    """Parse tfdragonn log file

    Args:
      path: file path to the log file

    Returns:
      pandas DataFrame
    """
    lines = read_txt(path)
    epochs = []
    auROCs = []
    auPRCs = []
    recalls = []
    num_positives_list = []
    num_negatives_list = []
    balanced_accuracies = []
    best_epoch = None
    arch_file = None
    weights_file = None
    for line in lines:
        if line.startswith("Epoch"):
            epochs.append(int(re.search('Epoch (.*):', line).group(1)))
        if line.startswith("Balanced Accuracy: "):
            balanced_accuracies.append(float(re.search('Balanced Accuracy: (.*)%\tauROC', line).group(1)) / 100)
            auROCs.append(float(re.search('auROC: (.*)\t auPRC', line).group(1)))
            auPRCs.append(float(re.search('auPRC: (.*)$', line).group(1)))
        if line.startswith("Recall at"):
            recalls.append(list(map(float, re.search('FDR: (.*)%\tNum', line).group(1).split("% | "))))
            num_positives_list.append(int(re.search('Num Positives: (.*)\t', line).group(1)))
            num_negatives_list.append(int(re.search('Num Negatives: (.*)$', line).group(1)))
        if line.startswith("The best model's architecture and weights"):
            best_epoch = int(re.search('\(from epoch (.*)\)', line).group(1))
            arch_file = re.search('were saved to (.*) and', line).group(1)
            weights_file = re.search('json and (.*)$', line).group(1)

    recalls = np.array(recalls)
    if len(epochs) == 0 and len(auROCs) > 0:
        epochs = [None] * len(auROCs)

    dfo = pd.DataFrame.from_items([("path", path),
                                    ("epoch", epochs),
                                    ("best_epoch", best_epoch),
                                    ("balanced_accuracy", balanced_accuracies),
                                    ("auROC", auROCs),
                                    ("auPRC", auPRCs),
                                    ("recall_at_5", recalls[:, 0]),
                                    ("recall_at_10", recalls[:, 1]),
                                    ("recall_at_25", recalls[:, 2]),
                                    ("recall_at_50", recalls[:, 3]),
                                    ("num_positives", num_positives_list),
                                    ("num_negatives", num_negatives_list),
                                    ("arch_file", arch_file),
                                    ("weights_file", weights_file),
                                    ])
    if best_epoch is None:
        dfo['best_epoch'] = dfo.iloc[dfo.auPRC.argmax()].epoch
    return dfo
    
