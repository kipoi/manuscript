# Note: all paths are relative w.r.t. repo root

DATA = "data/"
HOLDOUT_CHR = 'chr8'


FASTA=DATA+'raw/dataloader_files/shared/hg19.fa'
TF_C_pairs = [("CEBPB", "HeLa-S3"),
              ("JUND", "HepG2"),
              ("MAFK", "K562"),
              ("NANOG", "H1-hESC")]
TFS, CELL_TYPES = list(zip(*TF_C_pairs))
TF2CT = {tf: ct for tf, ct in TF_C_pairs}


# Models to run:
SINGLE_TASK_MODELS = {
    "CEBPB": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/CEBPB",
        "DeepBind": "DeepBind/D00317.009",
        "FactorNet": "FactorNet/CEBPB/meta_Unique35_DGF",
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
    },
    "JUND": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/JUND",
        "DeepBind": "DeepBind/D00776.005",
        "FactorNet": "FactorNet/JUND/meta_Unique35_DGF_2", # meta_Unique35_DGF_2
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Jund/Hepg2/Sydh_Iggrab",
        # HACK - TODO make this code more general. Allow running multiple
        # models for one TF
        "lsgkm-SVM2": "lsgkm-SVM/Tfbs/Jund/Hepg2/Haib_Pcr1x",
    },
    "MAFK": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/MAFK",
        "DeepBind": "DeepBind/D00503.014",
        "FactorNet": "FactorNet/MAFK/meta_1_Unique35_DGF",
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Mafkab50322/K562/Sydh_Iggrab",
    },
    "NANOG": {        
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/NANOG",
        "DeepBind": "DeepBind/D00786.001",
        "FactorNet": "FactorNet/NANOG/onePeak_Unique35_DGF", # GENCODE_Unique35_DGF
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Nanogsc33759/H1hesc/Haib_V0416102",
    }
}


# Evaluate the models - kwargs
def get_dl_kwargs(tf):
    """Returns the dataloader kwargs for each model"""
    cell_type = TF2CT[tf]
    intervals = DATA+"raw/tfbinding/eval/intervals/" + \
                "chr8_wide_bin101_flank0_stride101.{tf}.{ctype}.intervals_file.tsv".\
                format(tf=tf, ctype=cell_type)

    # FactorNet DNASE
    dnase = DATA+"raw/tfbinding/eval/DNASE/FactorNet/{ctype}.1x.bw".format(ctype=cell_type)

    # Default DREAM challenge
    # dnase = DATA+"raw/tfbinding/eval/DNASE/DNASE.{ctype}.fc.signal.bigwig".format(ctype=cell_type)

    return {"intervals_file": intervals,
            "dnase_file": dnase,
            "fasta_file": FASTA,
	        "cell_line": cell_type,
            "use_linecache": True
            }