


## Training models

### Randomly initialized

- get the model architecture from the existing model (from Kipoi) and re-train it
   - OR use it directly from TF-dragonn


### Transferred model

- get_model("Divergent")
- change the last layer
- re-train the model
  - save weights
  - save metrics (train and validation)


### Evaluate model

- take each model and evaluate it
  - Use Kipoi (?) to do so



## TODO

- [x] Split the whole datasets into train,valid,test and also into different tasks
  - Use Snakemake to do so
- [x] re-write a new dataloader which adopts to the number of output features (bed3 + features)
- [ ] tlearn.py
  - model
  - lr
  - patience
  - eval_metrics
  - early_stop_metric
  - freeze_to=layer
  - transfer_to=layer
  - add_n_hidden='[]'  # number of hidden layers to add
  - train_dl_kwargs (adopt to the new dataset)
    - intervals_file
    - fasta_file
  - valid_dl_kwargs
