"""
Snakefile for the splicing model
"""
ENVS = {"kipoi-var-effect": MODELS_FULL}

def get_env_executable(env):
    return os.path.abspath(os.path.join(sys.executable, "../../envs/{env}/bin/kipoi".format(env=env)))


# rule all:
#     input:
#         # dbscSNV data
#         "data/raw/splicing/dbscSNV/Supplementary_Table_S2.tsv",
#         "data/processed/splicing/dbscSNV/variants.vcf",
#         # Environment
#         # expand('data/envs/splicing/{env}.yml', env=list(ENVS)),
#         # [get_env_executable(env) for env in ENVS],
#         # ---
#         # annotated vcfs
#         expand("data/processed/splicing/dbscSNV/annotated_vcf/variants/{model}.vcf", model=MODELS),
#         "data/processed/splicing/dbscSNV/modeling_df.tsv"


rule download_dbscsnv:
    """Downloads paper's supplementary material from: https://academic.oup.com/nar/article/42/22/13534/2411339#supplementary-data"""
    output:
        xlsx = "data/raw/splicing/dbscSNV/Supplementary_Table_S1-S6.xlsx"
    shell:
        """
        # Download
        wget --header="Host: oup.silverchair-cdn.com" --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36" --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" --header="Accept-Language: en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,sl;q=0.6" "https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/nar/42/22/10.1093_nar_gku1206/2/gku1206_Supplementary_Data.zip?Expires=1524013830&Signature=41gGfX6sPUhBv0BtpZrAaRjsJBRexgAr6D17GcS1RMK64Xbo5-dm-KBdtW6HWAXfgsNbM~khkNl79elKf4aX--UAEmLBUS8zxyCe-RQKg9Ob~LE6EtFZhRGPOnDmS2f4nbcwgp-QPYloRLpPUog8NaOwpTBQk8jUEMACO0j-MXqXJqX7QJ~T80GYVOzjuoe~W~4O3YP5ITKPVvri1es5KLXDGldQWTQp67sQYF8ot2D-e46rS3w1C2yfZJ5RPGzb9we42YNr7Mh2lPoNmEXHlkAV7yoIEKWoVlq5LSKbVlHbPOfRBtoWllnMWe74RY1Hxmi~XdWTTdit0bcschIFFw__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA" -O gku1206_Supplementary_Data.zip -c
        # Extract
        unzip gku1206_Supplementary_Data.zip
        mv Supplementary_Table_S1-S6.xlsx {output.xlsx}
        # Cleanup
        rm gku1206_Supplementary_Data.zip
        """

rule download_dbscsnv_scores:
    output:
        f = "data/raw/splicing/dbscSNV/dbscSNV.chr1",
        z = temp("data/raw/splicing/dbscSNV/dbscSNV.zip")
    shell:
        """
        wget ftp://dbnsfp:dbnsfp@dbnsfp.softgenetics.com/dbscSNV.zip
        unzip dbscSNV.zip
        """

rule dbscsnv_xlsx2tsv:
    """extract the variant data from the excell sheet
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
    """Convert the dbscSNV tsv file to a vcf file"""
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

rule gzip_file:
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
        dfg = gather_vcfs(MODELS_FULL, base_path="data/processed/splicing/dbscSNV/annotated_vcf/variants/models", ncores=16)
        #
        dfm = get_dbscsnv_data()
        # assert dfm.shape[0] == dfg.shape[0]

        dfm['variant_id'] = dfm.Chr + ":" + dfm.Position.astype(str) + ":" + dfm.Ref + ":['" + dfm.Alt + "']"

        dfgm = dfm.merge(dfg, on='variant_id')
        assert dfgm.shape[0] == dfg.shape[0]
        dfgm.to_csv(output.tsv, sep='\t', index=False)
