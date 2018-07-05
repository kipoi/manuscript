"""
Snakefile for the splicing model
"""

rule download_clinvar:
    output:
        vcf = "data/raw/splicing/clinvar/{clinvar_file}.vcf.gz",
        vcf_tbi = "data/raw/splicing/clinvar/{clinvar_file}.vcf.gz.tbi",
    shell:
        """
        wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/archive_2.0/2018/clinvar_{wildcards.clinvar_file}.vcf.gz -O {output.vcf}
        wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/archive_2.0/2018/clinvar_{wildcards.clinvar_file}.vcf.gz.tbi -O {output.vcf_tbi}
        """

rule clinvar_donor_acceptor:
    """Generate the annotation bed files"""
    output:
        acceptors = "data/processed/splicing/clinvar/acceptors.bed",
        acceptors_num = "data/processed/splicing/clinvar/acceptors.numchr.bed",
        donors = "data/processed/splicing/clinvar/donors.bed",
        donors_num = "data/processed/splicing/clinvar/donors.numchr.bed"
    script:
        ROOT + "/src/splicing/generate_regions.R"


rule filter_vcf:
    """Restrict the variants only to the donor or acceptor sites
    """
    input:
        vcf = "data/raw/splicing/clinvar/{clinvar_file}.vcf.gz",
        acceptors_num = "data/processed/splicing/clinvar/acceptors.numchr.bed",
        donors_num = "data/processed/splicing/clinvar/donors.numchr.bed",
    output:
        vcf = "data/processed/splicing/clinvar/{clinvar_file}.filtered.vcf.gz",
        vcf_tbi = "data/processed/splicing/clinvar/{clinvar_file}.filtered.vcf.gz.tbi"
    shell:
        """
        vcftools --gzvcf {input.vcf} --remove-indels --recode --recode-INFO-all -c | \
            awk '$5 != "."' | \
            bedtools intersect -a stdin -b {input.acceptors_num} {input.donors_num} -wa -u -header | \
            bgzip -c > {output.vcf}
        tabix -f -p vcf {output.vcf}
        #awk '$1 ~ /^#/ {{print $0;next}} {{print $0 | "LC_ALL=C sort -k1,1 -k2,2n"}}' | \
        """

rule intersect_spidex:
    """Subset spidex to speedup dataloading
    """
    input:
        spidex = "data/raw/splicing/spidex/hg19_spidex.txt.gz",
        vcf = "data/processed/splicing/clinvar/{clinvar_file}.filtered.vcf.gz"
    output:
        spidex = "data/raw/splicing/spidex/hg19_spidex.clinvar_{clinvar_file}.txt"
    shell:
        """
        bedtools intersect -a {input.spidex} -b {input.vcf} -header -sorted > {output.spidex}
        """

rule clinvar_gather:
    """Gather model-annotated vcf's into a single table

    VEP annotated file: http://grch37.ensembl.org/Homo_sapiens/Tools/VEP/Ticket?tl=4iJskr0Rc1jxAf43
    """
    input:
        vcfs = expand("data/processed/splicing/clinvar/annotated_vcf/{{clinvar_file}}.filtered/models/{model}.vcf",
                      model=MODELS_FULL)
    output:
        tsv = "data/processed/splicing/clinvar/annotated_vcf/{clinvar_file}.filtered/modeling_df.tsv"
    threads:
        16
    run:
        from m_kipoi.exp.splicing.gather import gather_vcfs
        dfg = gather_vcfs(MODELS_FULL,
                          base_path=f"data/processed/splicing/clinvar/annotated_vcf/{CLINVAR}.filtered/models",
                          ncores=16)
        #
        dfg.to_csv(output.tsv, sep='\t', index=False)
