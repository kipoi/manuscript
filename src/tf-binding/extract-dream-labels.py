"""Extract DREAM labels for TF binding

Files:
- Nanog: https://www.synapse.org/#!Synapse:syn8442110
- CEBPB: https://www.synapse.org/#!Synapse:syn8442119
- JUND: https://www.synapse.org/#!Synapse:syn8442086

Steps:
1. subset to chr8
2. choose the right cell type
3. convert U,A,B to 0,-1,1
"""
from m_kipoi.config import get_data_dir
import pandas as pd
from pathlib import Path
from m_kipoi.exp.tfbinding.config import TF_C_pairs

ddir = get_data_dir()
tfdir = Path(f"{ddir}/raw/tfbinding/eval/tf-DREAM")

label_map = {"U": 0, "A": -1, "B": 1}


for tf in ['CEBPB', 'JUND', 'NANOG']:
    print(tf)
    df = pd.read_csv(tfdir / f'{tf}.train.labels.tsv.gz', sep='\t')

    # subset the table
    df = df[df.chr == 'chr8']
    assert cell_types[tf] in df
    df = df[['chr', 'start', 'stop', cell_types[tf]]]

    # map labels
    df[cell_types[tf]] = df[cell_types[tf]].map(label_map)

    # save to file
    df.to_csv(tfdir / f'DREAM.chr8.{tf}.{cell_types[tf]}.bed', sep='\t', index=False, header=None)