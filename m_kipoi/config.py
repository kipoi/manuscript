import os
import joblib

# Set of global configs
CHROMOSOMES = [str(x) for x in range(1, 23)] + ["M", "X", "Y"]


def get_data_dir():
    """Returns the data directory
    """
    import inspect
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    this_path = os.path.dirname(os.path.abspath(filename))
    DATA = os.path.join(this_path, "../data")
    if not os.path.exists(DATA):
        raise ValueError(DATA + " folder doesn't exist")
    return DATA


# setup cache
memory = joblib.Memory("/tmp/kipoi/", compress=5)


@memory.cache
def list_models(base_models):
    import kipoi
    dtm = kipoi.list_models()
    dtm = dtm[~dtm.model.str.contains("template")]
    dtm = dtm[dtm.source == 'kipoi']
    dtm = dtm[dtm.model.str.contains("|".join(base_models))]
    # use only the CpGenie/merged model
    dtm = dtm[~(dtm.model.str.contains("CpGenie") & ~dtm.model.str.contains("merged"))]
    MODELS = list(dtm.model)
    return MODELS


# hg19-based vcf header
VCF_HEADER = """##fileformat=VCFv4.0
##contig=<ID=1,length=249250621>
##contig=<ID=2,length=243199373>
##contig=<ID=3,length=198022430>
##contig=<ID=4,length=191154276>
##contig=<ID=5,length=180915260>
##contig=<ID=6,length=171115067>
##contig=<ID=7,length=159138663>
##contig=<ID=8,length=146364022>
##contig=<ID=9,length=141213431>
##contig=<ID=10,length=135534747>
##contig=<ID=11,length=135006516>
##contig=<ID=12,length=133851895>
##contig=<ID=13,length=115169878>
##contig=<ID=14,length=107349540>
##contig=<ID=15,length=102531392>
##contig=<ID=16,length=90354753>
##contig=<ID=17,length=81195210>
##contig=<ID=18,length=78077248>
##contig=<ID=19,length=59128983>
##contig=<ID=20,length=63025520>
##contig=<ID=21,length=48129895>
##contig=<ID=22,length=51304566>
##contig=<ID=X,length=155270560>
##contig=<ID=Y,length=59373566>
##contig=<ID=MT,length=16569>
"""
