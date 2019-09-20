"""
Jitter the positive labels by shifting the interval location +- 50bp
"""
import os
import random
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
        return [line]
    else:
        shift = random.randint(-50, 50)  # jitter +- 50
        return [f"{chr}\t{start + shift}\t{end + shift}\t{label}\n"]


if __name__ == '__main__':
    random.seed(42)
    for fpath in DATASETS['beer-300bp']['intervals'].values():
        print(f"fpath: {fpath}")
        with open(fpath, 'r') as f:
            with open(os.path.join(os.path.dirname(fpath), 'jittered', os.path.basename(fpath) + ".jittered-50bp.tsv"), 'w') as fw:
                for line in f:
                    output_lines = extend_lines(line)
                    fw.writelines(output_lines)
