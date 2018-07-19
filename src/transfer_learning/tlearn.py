#!/usr/bin/env python
"""Script for transfer learning

Should work with any Kipoi model of `type: keras`
"""
import json
import time
from pathlib import Path
import numpy as np
import kipoi
import argparse
from kipoi.cli.parser_utils import add_model, add_dataloader
from keras.models import Sequential, Model
from kipoi.utils import parse_json_file_str
import keras.layers as kl
from keras.optimizers import Adam
from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
import GPUtil


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
    parser = argparse.ArgumentParser(description='Transfer-learn a Keras model from Kipoi')
    add_model(parser)
    add_dataloader(parser, with_args=False)
    parser.add_argument('--dl_kwargs_train', help="training data-loader kwargs")
    parser.add_argument('--dl_kwargs_eval', help="Evaluation data-loader kwargs")
    parser.add_argument('-t', '--tasks', type=int, help='Number of transferred tasks')
    parser.add_argument('-o', '--output', help='Output file directory')
    parser.add_argument('--transfer_to', help='Layer to which to transfer the model')
    parser.add_argument('--freeze_to', default=None, help='Layer to including up to which to freeze all the layers')
    parser.add_argument('--add_n_hidden', default="", type=str,
                        help='Comma separated list of hidden layers to add')
    parser.add_argument('--batch_size', default=32, type=int, help='Number of transferred tasks')
    parser.add_argument('--lr', default=0.001, type=float, help='Learning rate')
    parser.add_argument("-n", "--num_workers", type=int, default=0,
                        help="Number of parallel workers for loading the dataset")
    parser.add_argument('-p', '--patience', default=10, type=int, help='Early stopping patience')
    parser.add_argument('--gpu', default=-1, type=int, help='Which gpu to use. If -1, determine automatically')
    args = parser.parse_args()
    dl_kwargs_train = parse_json_file_str(args.dl_kwargs_train)
    dl_kwargs_eval = parse_json_file_str(args.dl_kwargs_eval)
    if args.add_n_hidden == "":
        hidden = []
    else:
        hidden = [int(x) for x in args.add_n_hidden.split(",")]
    # -------
    odir = Path(args.output)
    odir.mkdir(parents=True, exist_ok=True)

    if args.gpu == -1:
        gpu = GPUtil.getFirstAvailable(attempts=3, includeNan=True)[0]
    else:
        gpu = args.gpu
    create_tf_session(gpu)

    # Get the model and the dataloader
    model = kipoi.get_model(args.model, args.source)
    if args.dataloader is not None:
        Dl = kipoi.get_dataloader_factory(args.dataloader, args.dataloader_source)
    else:
        Dl = model.default_dataloader

    if not model.type == "keras":
        raise ValueError("Only keras models are supported")

    dl_train = Dl(**dl_kwargs_train)
    dl_eval = Dl(**dl_kwargs_eval)

    # ---------------
    # Setup a new model

    # Transferred part
    tmodel = Model(model.model.inputs,
                   model.model.get_layer(args.transfer_to).output)

    # Freeze all the layers up to (including) the freeze_to layer
    if args.freeze_to is not None:
        for l in tmodel.layers:
            l.trainable = False
            if l.name == args.freeze_to:
                break

    # Top model
    top_model = Sequential()
    if hidden:
        for i, nh in enumerate(hidden):
            if i == 0:
                top_model.add(kl.Dense(nh, activation="relu",
                                       input_shape=tmodel.output_shape[1:])
                              )
            else:
                top_model.add(kl.Dense(nh, activation="relu"))
        top_model.add(kl.Dense(args.tasks,
                               activation="sigmoid"))
    else:
        top_model.add(kl.Dense(args.tasks,
                               activation="sigmoid",
                               input_shape=tmodel.output_shape[1:]))

    final_model = Sequential([tmodel, top_model])
    final_model.compile(Adam(args.lr), "binary_crossentropy")
    # ---------------
    dl_train.batch_train_iter(cycle=True, shuffle=True, batch_size=args.batch_size, num_workers=args.num_workers)

    # Train the model (using Keras 1.2.2)
    start_time = time.time()
    final_model.fit_generator(dl_train.batch_train_iter(cycle=True,
                                                        shuffle=True,
                                                        batch_size=args.batch_size,
                                                        num_workers=args.num_workers),
                              samples_per_epoch=len(dl_train),
                              callbacks=[
                                  EarlyStopping(patience=args.patience),
                                  CSVLogger(str(odir / "history.csv")),
                                  ModelCheckpoint(str(odir / "weights.{epoch:02d}.hdf5"))],
                              validation_data=dl_eval.batch_train_iter(cycle=True,
                                                                       shuffle=True,
                                                                       batch_size=args.batch_size,
                                                                       num_workers=args.num_workers),
                              nb_val_samples=len(dl_eval),
                              nb_epoch=100)
    duration = time.time() - start_time
    print("Total duration: {}".format(duration))

    try:
        metrics = {"duration": float(duration),
                   "gpu": int(gpu),
                   "num_workers": int(args.num_workers),
                   "batch_size": int(args.batch_size)}
        (odir / "stats.json").write_text(json.dumps(metrics))
    except:
        print("Failed to write {} to the file".format(metrics))
