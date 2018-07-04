"""Generic kipoi rule for annotating the vcf files
"""
from m_kipoi.utils import get_env_executable

ENV_NAME = "kipoi-splicing"


rule create__env:
    """Create one conda environment for all splicing models
    """
    output:
        env = get_env_executable(ENV_NAME)
    shell:
        "kipoi env create {MODELS_FULL} -e {ENV_NAME} --vep"


rule annotate_vcf:
    """Annotate the Vcf using Kipoi's score variants
    """
    input:
        vcf = "data/processed/splicing/{d}/{vcf_file}.vcf.gz",
        gtf = "data/raw/dataloader_files/shared/Homo_sapiens.GRCh37.75.filtered.gtf",
        fasta = "data/raw/dataloader_files/shared/hg19.fa",
        kipoi = get_env_executable(ENV_NAME)
    output:
        vcf = "data/processed/splicing/{d}/annotated_vcf/{vcf_file}/models/{model}.vcf"
    params:
        dl_kwargs = json.dumps({"gtf_file": os.path.abspath(GTF_FILE),
                                "fasta_file": os.path.abspath(FASTA_FILE)}),
    shell:
        """
        mkdir -p `dirname {output.vcf}`
        # export CUDA_VISIBLE_DEVICES={GPU}
        {input.kipoi} postproc score_variants \
            {wildcards.model} \
            --dataloader_args='{params.dl_kwargs}' \
            -i $PWD/{input.vcf} \
            -n 10 \
            -o $PWD/{output.vcf} \
            -s ref alt diff
        """
