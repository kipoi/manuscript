#-------------------------
# snakemake
out_acceptors <- snakemake@output[["acceptors"]]
out_acceptors_num_chr <- snakemake@output[["acceptors_num"]]
out_donors <- snakemake@output[["donors"]]
out_donors_num_chr <- snakemake@output[["donors_num"]]
#-------------------------
#' Libs
library(magrittr)
library(data.table)
library(TxDb.Hsapiens.UCSC.hg19.knownGene)
library(rtracklayer)
#-------------------------
# PARAMS
acceptor_range <- c(-40, 10)
donor_range <- c(-10, 10)
source("src/splicing/functions.R")
#-------------------------
introns <- intronsByTranscript(TxDb.Hsapiens.UCSC.hg19.knownGene) %>% unlist

acceptors <- resize(introns, 1, fix="end") %>%
  extend_range(-acceptor_range[1], acceptor_range[2])
donors <- resize(introns, 1, fix="start") %>%
  extend_range(-donor_range[1], donor_range[2])

# write out the acceptors and donors
export(acceptors, out_acceptors, format="bed")
export(donors, out_donors, format="bed")

# Convert to the numerical form
acceptors_form2 <- acceptors
donors_form2 <- donors
seqlevels(acceptors_form2) <- gsub("^chr", "", seqlevels(acceptors_form2))
seqlevels(donors_form2) <- gsub("^chr", "", seqlevels(donors_form2))

export(acceptors_form2, out_acceptors_num_chr, format="bed")
export(donors_form2, out_donors_num_chr, format="bed")
