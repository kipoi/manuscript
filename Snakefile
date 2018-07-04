"""Reproduce the whole analysis
"""
# other files
# include: "experiments/Snakefile"

import json
# TODO -
# - kipoi postproc score_variants
#   - why is there an --output flag?
#   - --out_vcf_fpath -> out_vcf
#   - rename args to: in_vcf, out_vcf (-iv, -ov) ?

# TODO - questions
#  - how to specify the fasta and how the bed file?

# Rules:
# 1. generate the environment yaml file for a model
# 2. run `kipoi postproc score_variants ...`
# 3. run merge table (in python)
#   - read vcf as a pandas.DataFrame
#   - merge the columns...
import kipoi
BASE_MODELS = ["DeepSEA/variantEffects", "CpGenie"]  # ALL
# BASE_MODELS = ["DeepSEA"]
# BASE_MODELS = ["rbp_eclip"]
dtm = kipoi.list_models()
dtm = dtm[~dtm.model.str.contains("template")]
dtm = dtm[dtm.source == 'kipoi']
dtm = dtm[dtm.model.str.contains("|".join(BASE_MODELS))]
# use only the CpGenie/merged model
dtm = dtm[~(dtm.model.str.contains("CpGenie") & ~dtm.model.str.contains("merged"))]
MODELS = list(dtm.model)

DATA = "data"

# MODELS = ["DeepSEA", "CpGenie/NT2_D1_ENCSR080YRO", "rbp_eclip/AARS"]
ENV_MODELS = ["DeepSEA/variantEffects", "CpGenie/NT2_D1_ENCSR080YRO", "rbp_eclip/AARS"]
VCF_FILE = ["deepsea_eqtl", "deepsea_gwas", "gkmsvm_meqtl"]
DSET = ["pos", "neg"]
EXTRA_VCF = "1Mrand1kg_bkg_neg"


# create only a single environment per parent group (for say )
def model_group2env_model(wildcards, model_group=None):
    """Maps the model model_group to base model
    """
    if model_group is None:
        print("wildcards")
        print(wildcards)
        model_group = wildcards.model_group
    for x in ENV_MODELS:
        if x.startswith(model_group):
            return x
    raise ValueError("model group {0} couln't be mapped to the right model".format(model_group))

def model2model_group(model):
    """Maps the model model_group to base model
    """
    if "/" in model:
        return os.path.dirname(model)
    else:
        return model


def get_condafile(wildcards):
    return DATA + "/envs/{0}.yaml".format(model2model_group(wildcards.model))


def get_env(wildcards):
    # Hacking required due to Snakemake bug
    # https://bitbucket.org/snakemake/snakemake/issues/728/allow-to-use-functions-for-specifying-the
    from kipoi.cli.env import conda_env_name
    dhash = {"DeepSEA": "a512028c",
             "conservation_imputed": "dcc3158b",
             "CpGenie": "413330db",
             "rbp_eclip": "dcc3158b",
             }
    if wildcards.model in dhash:
        return os.getcwd() + "/.snakemake/conda/" + dhash[model2model_group(wildcards.model)]
    else:
        return conda_env_name(wildcards.model, wildcards.model)

# rules ----------------------------------------------------


rule all:
    input:
        # enhanced vcf
        expand(DATA + "/processed/vcf/{model}/{vcf}_{dset}.vcf",
               model=MODELS,
               vcf=VCF_FILE,
               dset=DSET),
        expand(DATA + "/processed/vcf/{model}/{vcf}.vcf", model=MODELS, vcf=EXTRA_VCF),
        # vcf -> parquet
        expand(DATA + "/processed/modeling/design_matrix/{vcf}_{dset}.parquet", dset=DSET, vcf=VCF_FILE),
        expand(DATA + "/processed/modeling/design_matrix/{vcf}.parquet", vcf=[EXTRA_VCF]),



rule generate_env_file:
    """Generates the conda environment files
    """
    output:
        DATA + "/envs/{model_group}.yaml"
    params:
        model = model_group2env_model
    shell:
        "kipoi env export {params.model} -o {output}"



rule test_models:
    """Runs kipoi test
    """
    # conda:
    #    DATA + "/envs/{model}.yaml"
    output:
        log = DATA + "/processed/model_test/{model}/output.log",
    params:
        env = get_env
    shell:
        """
        echo "Activating: {params.env}"
        source activate {params.env}
        kipoi test {wildcards.model} --source=kipoi > {output.log}
        """

def get_args(wildcards):
    """Determine the right dataloader_args
    """
    model = wildcards.model
    if "rbp_eclip" in model:
        return '{"fasta_file": "' + DATA + '/raw/dataloader_files/shared/hg19.fa", ' + \
            '"gtf_file": "' + DATA + '/raw/dataloader_files/shared/Homo_sapiens.GRCh37.75.gtf", "use_linecache": True}'
    elif "DeepSEA" in model or "CpGenie" in model:
        return '{"fasta_file": "' + DATA + '/raw/dataloader_files/shared/hg19.fa", "use_linecache": True}'


rule score_variants_vcf_centered:
    """Runs the variant scoring.

    The extracted genomic ranges are vcf-centered
    """
    input:
        vcf = DATA + "/vcf/{vcf}_{dset}.vcf",
    params:
        dl_args = get_args,
        env = get_env
    resources:
        mem = 16000
    threads: 16
    # conda:
    #    "input.env"
    output:
        vcf = DATA + "/processed/vcf/{model}/{vcf}_{dset}.vcf"
    shell:
        """
        echo "Activating: {params.env}"
        # module load i12g/cudnn/8.0-6.0
        source activate {params.env}
        # # Sleep a bit in order to prevent crashing

        # if [ "{wildcards.vcf}" = "deepsea_eqtl" ]; then
        #     # sleep $[ ( $RANDOM % 10 )  + 1 ]s
        #     sleep 30s
        # fi
        # if [ "{wildcards.vcf}" = "deepsea_gwas" ]; then
        #     sleep 15s
        # fi
        # # Choose one GPU if it exists
        # eval `python bin/choose_gpu.py`
        # ----------------
        # TODO - update
        # source activate kipoi-CpGenie-manual
        # ----------------
        kipoi postproc score_variants {wildcards.model} \
          --vcf_path {input.vcf} \
          --dataloader_args='{params.dl_args}' \
          -a {output.vcf} \
          --batch_size 32 \
          -n 16 \
          --scoring deepsea_scr diff
        """


rule vcf2parquet:
    """Convert the vcf files to parquet file - merge accross different files
    """
    input:
        vcfs = [DATA + "/processed/vcf/" + model + "/{vcf}_{dset}.vcf"
                for model in MODELS + ["conservation_imputed"]],
        # vcf = DATA + "/processed/vcf/{model}/{vcf}_{dset}.vcf"
    output:
        parquet = DATA + "/processed/modeling/design_matrix/{vcf}_{dset}.parquet"
        # parquet = DATA + "/processed/parquet/{model}/{vcf}_{dset}.parquet"
    threads: 1
    run:
        from m_kipoi.parsers import KipoiVCFParser
        from m_kipoi.utils import write_parquet_iterable
        from functools import reduce

        def prepare(d):
            # d = flatten_dict(d)
            d["class_positive"] = wildcards.dset == "pos"
            d["variant_set"] = wildcards.vcf

            return d

        def merge_dict(a, b):
            # import pdb
            # pdb.set_trace()

            # check that variant id's are the same
            assert a["variant_id"] == b["variant_id"]
            return {**a, **b}

        it = map(lambda x: reduce(merge_dict, x),  # merge dicts
                 zip(*[map(prepare, KipoiVCFParser(f))
                       for f in input.vcfs])
                 )

        # TODO - handle also differerent datasets
        write_parquet_iterable(it,
                               output.parquet,
                               compression="SNAPPY",
                               chunksize=4096)
