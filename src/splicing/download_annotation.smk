"""Download the annotation files
"""

rule download_extract_filter_gtf:
    output:
        gtf = GTF_FILE
    shell:
        """wget -O - ftp://ftp.ensembl.org/pub/release-75/gtf/homo_sapiens/Homo_sapiens.GRCh37.75.gtf.gz | \
          zcat | \
          grep -v ^H | \
          grep -v ^GL  > {output.gtf}
        """
        #  awk '{{ if($1 !~ /^#/){{print "chr"$0}} else{{print $0}} }}' > {output.gtf}
        # """

rule download_extract_fasta:
    """This will replace the headers in the ensembl fasta file from:
    >1 dna:chromosome chromosome:GRC ...
    to
    >chr1
    """
    output:
        fa = FASTA_FILE
    shell:
        "wget -O - ftp://ftp.ensembl.org/pub/release-75/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa.gz |"
        "zcat | sed 's/\s.*$//' > {output.fa}"
        # sed  -e 's/^>/>chr/' |
