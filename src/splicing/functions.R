
#' get the clinvar data.table
get_clinvar_dt<- function(path="data/raw/clinvar/variant_summary_2016-09.csv") {
  cv <- fread(path)[Assembly == "GRCh37"]
  cv[, chr := paste0("chr", Chromosome)]
  cv[, chr := gsub("chrMT", "chrM", chr)]
  cv[, Chromosome := NULL]
  setnames(cv, c("Start", "Stop"), c("start", "end"))
  return(cv)
}


##' Extend (pad) the granges range some bases upstream and some downstream wrt the strand
##' 
##' @param n_upstream Number of bases to extend upstream. 0 is the neutral element
##' @param n_upstream Number of bases to extend downstream. 0 is the neutral element
##' @return granges with extended start and stop with respect to the strand
extend_range <- function(gr, n_upstream = 0, n_downstream = 0) {
  gr <- copy(gr)
  gr <- resize(gr, width(gr) + n_downstream, fix = "start")
  gr <- resize(gr, width(gr) + n_upstream, fix = "end")
  return(gr)
}


#' add a column `in_exon` to a granges in case
#' the variant is found in the exon
#' @param gr granges of interest
#' @param gr_exons granges of exons obtained
#' by exons(TxDb.Hsapiens.UCSC.hg38.knownGene)
add_in_exon <- function(gr, gr_exons) {
  ol <- findOverlaps(gr, gr_exons)
  gr$in_exon <- FALSE
  gr$in_exon[queryHits(ol)] <- TRUE
  return(gr)
}


## dt_anno <- dt_anno %>% setkeyv(c("seqnames", "strand", "gene_id", "start"))
## dt_peak <- dt_peak %>% setkeyv(c("seqnames", "strand", "gene_id", "start"))
## dt_peak_closest <- dt_anno[dt_peak, roll="nearest"] %>% setkey(NULL) %>% unique

## dist_to_intron_exon <- function(gr, gr_exons) {
##   ie <- resize(ex, width=1, fix="start")
  
## }
