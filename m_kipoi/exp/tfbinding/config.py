# Note: all paths are relative w.r.t. repo root

DATA = "data/"
HOLDOUT_CHR = 'chr8'

ANNO = DATA + "raw/dataloader_files/shared"
NUM_FASTA_FILE = f"{ANNO}/hg19.fa"
CHR_FASTA_FILE = f"{ANNO}/hg19.w-chr.fa"

# FASTA = DATA + 'raw/dataloader_files/shared/hg19.fa'
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
        "DeepBind": "DeepBind/Homo_sapiens/TF/D00317.009_ChIP-seq_CEBPB",
        "FactorNet": "FactorNet/CEBPB/meta_Unique35_DGF",
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
        "lsgkm-SVM-1kb": "lsgkm-SVM-1kb/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
        "lsgkm-SVM-retrained": "lsgkm-SVM-retrained/Tfbs/Cebpb/Helas3/Sydh_Iggrab",
    },
    "JUND": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/JUND",
        "DeepBind": "DeepBind/Homo_sapiens/TF/D00776.005_ChIP-seq_JUND",
        "FactorNet": "FactorNet/JUND/meta_Unique35_DGF_2",  # meta_Unique35_DGF_2
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Jund/Hepg2/Sydh_Iggrab",
        "lsgkm-SVM-retrained": "lsgkm-SVM-retrained/Tfbs/Jund/Hepg2/Sydh_Iggrab",
    },
    "MAFK": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/MAFK",
        "DeepBind": "DeepBind/Homo_sapiens/TF/D00503.014_ChIP-seq_MAFK",
        "FactorNet": "FactorNet/MAFK/meta_1_Unique35_DGF",
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Mafkab50322/K562/Sydh_Iggrab",
        "lsgkm-SVM-retrained": "lsgkm-SVM-retrained/Tfbs/Mafkab50322/K562/Sydh_Iggrab",
    },
    "NANOG": {
        "pwm_HOCOMOCO": "pwm_HOCOMOCO/human/NANOG",
        "DeepBind": "DeepBind/Homo_sapiens/TF/D00786.001_ChIP-seq_NANOG",
        "FactorNet": "FactorNet/NANOG/onePeak_Unique35_DGF",  # GENCODE_Unique35_DGF
        "DeepSEA": "DeepSEA/predict",
        "lsgkm-SVM": "lsgkm-SVM/Tfbs/Nanogsc33759/H1hesc/Haib_V0416102",
        "lsgkm-SVM-retrained": "lsgkm-SVM-retrained/Tfbs/Nanogsc33759/H1hesc/Haib_V0416102",
    }
}


# Evaluate the models - kwargs
def get_dl_kwargs(tf):
    """Returns the dataloader kwargs for each model"""
    cell_type = TF2CT[tf]
    intervals = DATA + "raw/tfbinding/eval/tf-DREAM/" + \
        "chr8_wide_bin101_flank0_stride101.{tf}.{ctype}.intervals_file.tsv".\
        format(tf=tf, ctype=cell_type)

    # FactorNet DNASE
    dnase = DATA + "raw/tfbinding/eval/DNASE/FactorNet/{ctype}.1x.bw".format(ctype=cell_type)

    return {"intervals_file": intervals,
            "dnase_file": dnase,
            "fasta_file": CHR_FASTA_FILE,
            "cell_line": cell_type,
            "use_linecache": True
            }


def get_dl_kwargs_DREAM(tf):
    """Returns the dataloader kwargs for each model"""
    cell_type = TF2CT[tf]
    intervals = DATA + f"raw/tfbinding/eval/tf-DREAM/DREAM.chr8.{tf}.{cell_type}.bed"

    # FactorNet DNASE
    dnase = DATA + "raw/tfbinding/eval/DNASE/FactorNet/{ctype}.1x.bw".format(ctype=cell_type)

    return {"intervals_file": intervals,
            "dnase_file": dnase,
            "fasta_file": CHR_FASTA_FILE,
            "cell_line": cell_type,
            "use_linecache": True
            }