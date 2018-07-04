"""Compute distance
"""
import os
from m_kipoi.config import get_data_dir
import numpy as np
import logging
import bcolz
from scipy.spatial.distance import pdist
from m_kipoi.utils import write_bcolz, read_bcolz
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

ddir = get_data_dir()

logging.info("Loading the txt file")


# -----------


bc_path = os.path.join(ddir, "processed/tlearn/clustering/cell_array_transposed.bc")
if not os.path.exists(bc_path):
    logging.info("Writing the bcolz file")
    import pandas as pd
    df = pd.read_csv(os.path.join(ddir, "raw/tlearn/clustering/cell_array_transposed.csv"), dtype=bool, header=None)
    X = df.values
    # X = np.loadtxt(os.path.join(ddir, "raw/tlearn/clustering/cell_array_transposed.csv"), dtype=bool, delimiter=",")
    write_bcolz(bc_path, X)
else:
    logging.info("Loading the matrix from the bcolz file")
    X = read_bcolz(bc_path)

# -----------

logging.info("Computing the jaccard distance")
d_jaccard = pdist(X, metric='jaccard')

logging.info("Writing the metric to file")
np.savetxt(os.path.join(ddir, "processed/tlearn/dist/jaccard.txt"), d_jaccard)

# -----------
logging.info("Computing the cosine distance")
d_cosine = pdist(X, metric='cosine')

logging.info("Writing it to file")
np.savetxt(os.path.join(ddir, "processed/tlearn/dist/cosine.txt"), d_cosine)

logging.info("Done!")
