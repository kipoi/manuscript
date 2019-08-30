"""
Snakefile for the splicing model
"""
workdir:
    "../../"
ROOT = "../.."
DATA = "data/"

import matplotlib
matplotlib.use('Agg')
import sys
from kipoi.cli.env import get_env_name
from glob import glob

# Folder structure for data:
# - raw: raw/tfbinding/eval-DREAM/<task>/files...
# - processed:
#   - processed/tfbinding/eval-DREAM/preds/
#   - processed/tfbinding/eval-DREAM/metrics/
#   - processed/tfbinding/eval-DREAM/plots/

# --------------------------------------------
# Config
from m_kipoi.utils import get_env_executable
from m_kipoi.exp.tfbinding.config import (DATA, TF_C_pairs, TFS, CELL_TYPES,
                                          NUM_FASTA_FILE, CHR_FASTA_FILE,
                                          HOLDOUT_CHR, TF2CT, SINGLE_TASK_MODELS,
                                          get_dl_kwargs_DREAM)


# Exclude MAFK for now
TF_C_pairs = [("CEBPB", "HeLa-S3"),
              ("JUND", "HepG2"),
              # ("MAFK", "K562"),
              ("NANOG", "H1-hESC")]
TFS, CELL_TYPES = list(zip(*TF_C_pairs))
TF2CT = {tf: ct for tf, ct in TF_C_pairs}
SINGLE_TASK_MODELS = {k: v for k,v in SINGLE_TASK_MODELS.items() if k in TFS}


# in the new API, we could also use a single name for the model
ENVIRONMENTS = {
    "DeepSEA": "DeepSEA/predict",
    "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/CEBPB",
    "DeepBind": "DeepBind/Homo_sapiens/TF/D00317.009_ChIP-seq_CEBPB",
    "FactorNet": "FactorNet/JUND/meta_Unique35_DGF",
    "lsgkm-SVM": "lsgkm-SVM/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
    "lsgkm-SVM-1kb": "lsgkm-SVM/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
}

ENVIRONMENT_NAMES = {
    "DeepSEA": "DeepSEA",
    "pwm_HOCOMOCO": "pwm_HOCOMOCO",
    "DeepBind": "DeepBind",
    "FactorNet": "FactorNet",
    "lsgkm-SVM": "lsgkm-SVM",
    "lsgkm-SVM-1kb": "lsgkm-SVM",
}
# --------------------------------------------


rule all:
    input:
        # Raw data
        expand(DATA + "raw/tfbinding/eval/tf-DREAM/" +
               "chr8_wide_bin101_flank0_stride101.{tf}.{ctype}.intervals_file.tsv.gz",
               zip, tf=TFS, ctype=CELL_TYPES),
        # FactorNet DNase
        expand(DATA + "raw/tfbinding/eval/DNASE/FactorNet/{ctype}.1x.bw", ctype=CELL_TYPES),
        # Environments
        [get_env_executable(env) for env in ENVIRONMENTS],

        # predictions
        [DATA + "processed/tfbinding/eval-DREAM/preds/{tf}/{model}.h5".format(tf=tf, model=model)
         for tf, value in SINGLE_TASK_MODELS.items()
         for model, model_name in value.items()
         if model_name is not None],

        # metrics
        "data/processed/tfbinding/eval-DREAM/metrics/all_models.chr8.csv",

        # plots
        expand("data/processed/tfbinding/eval-DREAM/plots/all_models.chr8.{fmt}",
               fmt=['pdf', 'png'])

# --------------------------------------------
# Evaluate the models
rule predict:
    """Run model prediction"""
    input:
        kipoi = lambda w: get_env_executable(ENVIRONMENT_NAMES[w.model]),
        intervals = lambda w: get_dl_kwargs_DREAM(w.tf)['intervals_file'],
        fasta = lambda w: get_dl_kwargs_DREAM(w.tf)['fasta_file'],
        dnase_file = lambda w: get_dl_kwargs_DREAM(w.tf)['dnase_file'],
    output:
        preds = DATA + "processed/tfbinding/eval-DREAM/preds/{tf}/{model}.h5"
    params:
        model = lambda w: SINGLE_TASK_MODELS[w.tf][w.model],
        dl_kwargs = lambda w: get_dl_kwargs_DREAM(w.tf),
        batch_size = lambda w: 1024 if w.model.startswith("lsgkm-SVM") else 256,
        env_name = lambda w: ENVIRONMENT_NAMES[w.model],
        gpu = config['gpu']
    threads: 8
    resources:
        gpu = lambda w: 1 if w.model.split("/")[0] in ['DeepSEA', 'DeepBind', 'FactorNet'] else 0
    shell:
        """
        echo batch size: {params.batch_size}
        echo model: {wildcards.model}
        export CUDA_VISIBLE_DEVICES={params.gpu}
        {input.kipoi} predict {params.model} \
            --dataloader_args="{params.dl_kwargs}" \
            --batch_size={params.batch_size} \
            -n 1 \
            -o {output.preds}
        """


rule evaluate_models:
    """Gather model predictions and compute auPRC"""
    input:
        preds = [DATA + "processed/tfbinding/eval-DREAM/preds/{tf}/{model}.h5".format(tf=tf, model=model)
                 for tf, value in SINGLE_TASK_MODELS.items()
                 for model, model_name in value.items()
                 if model_name is not None]
    output:
        csv = "data/processed/tfbinding/eval-DREAM/metrics/all_models.chr8.csv"
    run:
        import pandas as pd
        from joblib import Parallel, delayed
        from m_kipoi.exp.tfbinding.eval import eval_model
        from tqdm import tqdm
        from m_kipoi.metrics import classification_metrics
        MODELS = ['pwm_HOCOMOCO', 'DeepBind', 'lsgkm-SVM', 'lsgkm-SVM-1kb', 'DeepSEA', 'FactorNet']
        df = pd.DataFrame(Parallel(n_jobs=32)(delayed(eval_model)(tf, model, classification_metrics,
                                                                  filter_dnase=filter_dnase)
                                              for model in tqdm(MODELS)
                                              for tf in tqdm(TFS)
                                              for filter_dnase in [True, False]))
        # Make a nice column description
        df['dataset'] = "Chromosome wide (chr8))"
        df['dataset'][df.filter_dnase == True] = "Only accessible regions (chr8))"
        df.to_csv(output.csv)


rule plot:
    """Create the plot"""
    input:
        csv = "data/processed/tfbinding/eval-DREAM/metrics/all_models.chr8.csv"
    output:
        files_all = expand("data/processed/tfbinding/eval-DREAM/plots/all_models.chr8.{fmt}",
                           fmt=['pdf', 'png']),
        files_dnase = expand("data/processed/tfbinding/eval-DREAM/plots/all_models.chr8.DNASE-peaks.{fmt}",
                             fmt=['pdf', 'png'])
    run:
        import matplotlib
        matplotlib.use('Agg')
        matplotlib.rcParams['pdf.fonttype'] = 42
        matplotlib.rcParams['ps.fonttype'] = 42
        import pandas as pd
        import seaborn as sns

        sns.set_context("talk")
        df = pd.read_csv(input.csv)
        pallete = ['#8dd3c7', '#fdb462', '#bebada', '#fb8072', '#80b1d3']
        df = df.rename(columns={"model": "Model"})

        # filter_dnase=False
        g = sns.factorplot(x="tf", y="auPR", hue="Model", data=df[~df.filter_dnase],
                           size=5, kind="bar", palette=pallete)
        g.set_xlabels("Transcription Factor")
        g.set_ylabels("auPRC")
        for fname in output.files_all:
            g.savefig(fname)

        # filter_dnase=True
        g = sns.factorplot(x="tf", y="auPR", hue="Model", data=df[df.filter_dnase],
                           size=5, kind="bar", palette=pallete)
        g.set_xlabels("Transcription Factor")
        g.set_ylabels("auPRC")
        for fname in output.files_dnase:
            g.savefig(fname)