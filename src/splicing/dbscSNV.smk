"""
Snakefile for the splicing model
"""
ENVS = {"kipoi-var-effect": MODELS_FULL}

def get_env_executable(env):
    return os.path.abspath(os.path.join(sys.executable, "../../envs/{env}/bin/kipoi".format(env=env)))


rule dbscsnv_xlsx2tsv:
    """Extract the variant data from the excel sheet

    The input file is already provided in data/. It was downloaded from 
    paper's supplementary material: https://academic.oup.com/nar/article/42/22/13534/2411339#supplementary-data
    """
    input:
        in_xlsx = "data/raw/splicing/dbscSNV/Supplementary_Table_S1-S6.xlsx"
    output:
        out_tsv = "data/raw/splicing/dbscSNV/Supplementary_Table_S2.tsv"
    run:
        import pandas as pd
        from openpyxl import load_workbook
        wb = load_workbook(input.in_xlsx)

        it = iter(wb["Table S2"].values)
        _ = next(it)
        header = next(it)

        df = pd.DataFrame(it, columns=header)
        # Cleanup
        df = df.rename(columns={"Splice site": "Splice_site"})

        df.to_csv(output.out_tsv, sep='\t')


rule dbscsnv2vcf:
    """Convert the dbscSNV tsv to a vcf file
    """
    input:
        in_tsv = "data/raw/splicing/dbscSNV/Supplementary_Table_S2.tsv"
    output:
        vcf = temp("data/processed/splicing/dbscSNV/variants.vcf")
    run:
        import pandas as pd
        import numpy as np
        from m_kipoi.config import VCF_HEADER  # hg19 based
        from collections import OrderedDict

        df = pd.read_csv(input.in_tsv, sep="\t")
        # Write the header
        with open(output.vcf, "w") as f:
            f.write(VCF_HEADER)

        # Append the variants
        variant_id = df.Chr.astype(str) + ":" + df.Position.astype(str) + ":" + df.Ref + ":['" + df.Alt + "']"
        pd.DataFrame(OrderedDict([("#CHROM", df.Chr.astype(str)),
                                  ("POS", df.Position),
                                  ("ID", variant_id),
                                  ("REF", df.Ref),
                                  ("ALT", df.Alt),
                                  ("QUAL", "."),
                                  ("FILTER", "."),
                                  ("INFO", "."),
                                  ])).to_csv(output.vcf, mode='a', header=True, index=False, sep="\t")

rule tabix_vcf:
    """Tabix the vcf
    """
    input:
        vcf = "data/processed/splicing/dbscSNV/variants.vcf"
    output:
        vcf_gz = "data/processed/splicing/dbscSNV/variants.vcf.gz",
    shell:
        """
        # Sort the vcf file
        bgzip -c {input.vcf} > {output.vcf_gz}
        tabix -f -p vcf {output.vcf_gz}
        """

rule intersect_spidex2:
    """Filters the spidex index to speedup dataloading
    """
    input:
        spidex = "data/raw/splicing/spidex/hg19_spidex.txt.gz",
        vcf = "data/processed/splicing/dbscSNV/variants.vcf.gz"
    output:
        spidex = "data/raw/splicing/spidex/hg19_spidex.dbscSNV.txt"
    shell:
        """
        bedtools intersect -a {input.spidex} -b {input.vcf} -header -sorted > {output.spidex}
        """

rule download_dbscsnv_scores:
    """Get the pre-computed dbscSNV scores
    """
    output:
        f = "data/raw/splicing/dbscSNV/dbscSNV.chr1",
        z = temp("data/raw/splicing/dbscSNV/dbscSNV.zip")
    shell:
        """
        # Note, if this doesn't work then manually download the file from
        # https://drive.google.com/uc?id=0B60wROKy6OqcZkw2bWt2TGU5NDA&export=download
        wget ftp://dbnsfp:dbnsfp@dbnsfp.softgenetics.com/dbscSNV.zip
        unzip dbscSNV.zip
        """


rule dbscsnv_gather:
    input:
        vcfs = expand("data/processed/splicing/dbscSNV/annotated_vcf/variants/models/{model}.vcf", model=MODELS_FULL)
    output:
        tsv = "data/processed/splicing/dbscSNV/modeling_df.tsv"
    threads:
        16
    run:
        from m_kipoi.exp.splicing.gather import gather_vcfs
        from m_kipoi.exp.splicing.data import get_dbscsnv_data
        dfg = gather_vcfs(MODELS_FULL,
                          base_path="data/processed/splicing/dbscSNV/annotated_vcf/variants/models",
                          ncores=16)
        #
        dfm = get_dbscsnv_data()
        # assert dfm.shape[0] == dfg.shape[0]

        dfm['variant_id'] = dfm.Chr + ":" + dfm.Position.astype(str) + ":" + dfm.Ref + ":['" + dfm.Alt + "']"

        dfgm = dfm.merge(dfg, on='variant_id')
        assert dfgm.shape[0] == dfg.shape[0]
        dfgm.to_csv(output.tsv, sep='\t', index=False)
