# session: sle-gwas-hpc (2026-09-08)

Raw provenance log for a real, unrelated working session used as brainny's
second dogfood test (first cross-domain test, per SEED.md Layer 7) -- not a
brainny-design session at all.

Project nature (inferred, none supplied): bioinformatics/genomics GWAS
pipeline engineering on an HPC/SLURM cluster (Snakemake-based fine-mapping,
enhancer-gene linking, local ancestry inference, heritability estimation);
reusable = pipeline techniques, HPC/SLURM/Snakemake gotchas, genotype-merge
decisions, and cluster job-orchestration precautions.

Summary: updated a SuSiEx+SuSiE-R fine-mapping pipeline and an scE2G
enhancer-gene-linking pipeline to a newly expanded 5-cohort Hispanic+Yucatan
GWAS cohort (rebuilding a merged in-sample LD panel, fixing sample sizes,
dropping FINEMAP), copied final deliverables into a manuscript archive and
built several new manuscript/supplementary tables, extended a local-ancestry
(RFMix/Tractor) case-control disease-risk analysis to 4 then 5 novel GWAS
loci scoped to +/-10Mb windows, and reran heritability estimation (GCTA
GREML) for the updated cohort -- diagnosing and fixing several Snakemake/
SLURM/PLINK issues along the way, including a GRM job that ran past its
6-hour time limit and had to be cancelled and resubmitted with a larger,
correctly-matched time budget.
