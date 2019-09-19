"""
Extend the resolution of the 300bp labels

Run this script from the repository root
"""
import os
from m_kipoi.exp.tfbinding.config import (DATA, TF_C_pairs, TFS, CELL_TYPES,
                                          DATASETS,
                                          NUM_FASTA_FILE, CHR_FASTA_FILE,
                                          HOLDOUT_CHR, TF2CT, SINGLE_TASK_MODELS)


def extend_lines(line):
    chr, start, end, label = line.split("\t")
    start = int(start)
    end = int(end)
    label = int(label)
    assert end - start == 300  # intervals have to be 300 bp in size
    if label == 0:
        return [f"{chr}\t{start + shift}\t{start + 100 + shift}\t{label}\n"
                for shift in [0, 100, 200]]
    else:
        return [f"{chr}\t{start + shift}\t{start + 100 + shift}\t{label}\n"
                for shift, label in [(0, 0),
                                     (100, 1),
                                     (200, 0)]]


# fpath = '/data/ouga04b/ag_gagneur/project_local/avsec/kipoi/manuscript/data/raw/tfbinding/eval/Beer-tfbinding/chr8_300.JUND.HepG2.intervals_file.tsv'

if __name__ == '__main__':
    for fpath in DATASETS['beer-300bp']['intervals'].values():
        print(f"fpath: {fpath}")
        with open(fpath, 'r') as f:
            with open(os.path.join(os.path.dirname(fpath), 'extended', os.path.basename(fpath) + ".extended-100bp.tsv"), 'w') as fw:
                for line in f:
                    output_lines = extend_lines(line)
                    fw.writelines(output_lines)
