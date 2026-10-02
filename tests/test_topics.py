from brainny.topics import normalize_domain, topic_of


def test_normalize_domain_is_formatting_only():
    assert normalize_domain("GWAS / LD  Score") == "gwas/ld score"
    assert normalize_domain("  dev tooling ") == "dev tooling"
    assert normalize_domain("/hpc/") == "hpc"
    assert normalize_domain("") == "uncategorized"


def test_topic_buckets_spelling_variants_together():
    for d in ["gwas/qc", "GWAS / LD", "gwas / summary-statistics harmonization", "statistical genetics/numerics",
              "Polygenic Risk Score (PRS) pipelines"]:
        assert topic_of(d) == "gwas", d
    assert topic_of("hpc-cluster-ops") == topic_of("hpc/slurm") == "hpc"
    assert topic_of("python-windows-encoding") == "windows & shell"
    assert topic_of("python packaging") == "python"


def test_unmatched_domain_keeps_its_own_first_segment():
    assert topic_of("Clawbio / contributing") == "clawbio"
