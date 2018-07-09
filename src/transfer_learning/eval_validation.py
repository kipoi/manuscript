#!/usr/bin/env python
"""Script for transfer learning
"""
import json
import time
from pathlib import Path
import numpy as np
import kipoi
import argparse
from kipoi.cli.parser_utils import add_model, add_dataloader
from keras.models import load_model
from kipoi.data_utils import numpy_collate_concat
from tqdm import tqdm
from kipoi.utils import parse_json_file_str
import keras.layers as kl
from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
import GPUtil
from eval_metrics import auprc, auc, accuracy


def create_tf_session(visiblegpus, per_process_gpu_memory_fraction=0.45):
    import os
    import tensorflow as tf
    import keras.backend as K
    os.environ['CUDA_VISIBLE_DEVICES'] = str(visiblegpus)
    session_config = tf.ConfigProto()
    session_config.gpu_options.per_process_gpu_memory_fraction = per_process_gpu_memory_fraction
    session = tf.Session(config=session_config)
    K.set_session(session)
    return session


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate the Keras Model')
    parser.add_argument('--model', help="Model path")
    add_dataloader(parser, with_args=False)
    parser.add_argument('--intervals_file', help="Intervals tsv file")
    parser.add_argument('--fasta_file', help="Fasta file")
    parser.add_argument('-o', '--output', help='Output json file')
    parser.add_argument('--batch_size', default=32, type=int, help='Number of transferred tasks')
    parser.add_argument("-n", "--num_workers", type=int, default=0,
                        help="Number of parallel workers for loading the dataset")
    parser.add_argument('--gpu', default=-1, type=int, help='Which gpu to use. If -1, determine automatically')
    args = parser.parse_args()
    # -------
    output = Path(args.output)
    # odir.mkdir(parents=True, exist_ok=True)

    if args.gpu == -1:
        gpu = GPUtil.getFirstAvailable(attempts=3, includeNan=True)[0]
    else:
        gpu = args.gpu
    create_tf_session(gpu)

    model = load_model(args.model)
    # Get the dataloader
    Dl = kipoi.get_dataloader_factory(args.dataloader, args.dataloader_source)
    dl = Dl(intervals_file=args.intervals_file,
            fasta_file=args.fasta_file,
            num_chr_fasta=True)

    metric_fns = {"auprc": auprc,
                  "auc": auc,
                  "accuracy": accuracy}
    
    y_true = dl.tsv.df[3].values
    y_pred = numpy_collate_concat([model.predict_on_batch(x['inputs'])
                                   for x in tqdm(dl.batch_iter(batch_size=args.batch_size,
                                                               num_workers=args.num_workers))])
    
    # ---------------
    metrics = {k: m(np.ravel(y_true), np.ravel(y_pred)) for k,m in metric_fns.items()}
    output.write_text(json.dumps(metrics))
