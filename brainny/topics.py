"""Domain hygiene + coarse topics for grouping.

`domain` is free text written by whichever AI session captured the idea,
so the same area shows up spelled many ways ("gwas/qc", "GWAS / LD",
"gwas / summary-statistics harmonization"). On a real central brain that
meant 136 domains for 209 ideas -- 103 of them singletons -- which left
every domain-clustered view (graph, treemap, cluster table) with nothing
to cluster. Two fixes, at two levels:

- `normalize_domain()`: formatting only (case, whitespace, one "/"
  separator). Applied at capture time and when rendering, so old data
  benefits too. Never changes meaning.
- `topic_of()`: a coarse, keyword-based bucket (gwas, hpc, pipelines, ...)
  used as the dashboard's default grouping. Unmatched domains fall back to
  their own first segment, so nothing is ever forced into a wrong bucket --
  it just stays its own small topic.
"""

from __future__ import annotations

import re

# Ordered: first match wins. Patterns match anywhere in the normalized
# domain, on word-ish boundaries, so "gwas/fine-mapping" -> gwas and
# "python-windows-encoding" -> windows & shell (windows before python).
TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("brainny", ("brainny",)),
    ("gwas", ("gwas", "fine-mapping", "finemapping", "colocali", "polygenic", "prs", "summary-statistic",
              "statistical genetics", "heritability", "ldsc", "meta-analysis", "mr-mega")),
    ("population genetics", ("population-genetic", "population genetic", "ancestry", "admixture", "phasing",
                             "imputation")),
    ("hpc", ("hpc", "slurm", "cluster-ops", "pbs")),
    ("ai & llm", ("llm", "prompt", "claude", "agent", "crazyai", "code generation", "ideation")),
    ("windows & shell", ("windows", "bash", "powershell", "shell")),
    ("pipelines", ("snakemake", "pipeline", "workflow", "nextflow")),
    ("bioinformatics", ("bioinformatic", "genomic", "vcf", "sequenc")),
    ("python", ("python", "pip", "packaging")),
    ("statistics", ("statistic", "model-validation", "experiment")),
    ("visualization & web", ("visuali", "figure", "plot", "matplotlib", "web", "frontend", "html",
                             "presentation", "image")),
    ("android & java", ("android", "java")),
    ("data", ("data", "spreadsheet", "sync")),
    ("research practice", ("reproducib", "provenance", "research", "peer review")),
    ("software engineering", ("software", "tooling", "testing", "test", "devops", "github", "build",
                              "documentation", "benchmark", "design", "maintenance", "cli")),
]


def normalize_domain(domain: str) -> str:
    d = (domain or "").strip().lower()
    d = re.sub(r"\s*/\s*", "/", d)
    d = re.sub(r"\s+", " ", d)
    d = d.strip("/")
    return d or "uncategorized"


def topic_of(domain: str) -> str:
    d = normalize_domain(domain)
    for topic, needles in TOPIC_RULES:
        if any(needle in d for needle in needles):
            return topic
    return d.split("/")[0]
