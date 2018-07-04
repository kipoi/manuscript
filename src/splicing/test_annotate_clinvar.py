from annotate_clinvar import *



def test_mutate_snp_seq():
    assert mutate_snp_seq(3, "C", "G",
                          Interval("chr1", 2, 5),
                          "ACGTA") == 'AGGTA'
    assert mutate_snp_seq(3, "A", "G",
                          Interval("chr1", 2, 6, strand="-"),
                          "ACGTA") == 'ACGCA'

    
