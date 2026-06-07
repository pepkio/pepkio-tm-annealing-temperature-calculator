# Pepkio Tm / Annealing Temperature Calculator

Run the Pepkio Tm / Annealing Temperature Calculator CLI in a fixed container environment to obtain per-primer melting temperatures, polymerase-specific annealing suggestions, and hairpin/dimer QC flags through the hosted API.

# What It Does

The image runs `pepkio-tm-annealing-temperature-calculator`, a client for the Pepkio Tm / Annealing Temperature Calculator REST API. Submit one primer pair or a batch of up to 200 pairs with a polymerase preset (Q5, Phusion, Taq, KAPA HiFi, or custom Na⁺ and Mg²⁺); receive per-primer Tm, ΔTm, suggested Ta, GC%, hairpin and dimer QC, Go/Flag/Fail status, method comparison values, and shareable permalinks.

Typical workflows include PCR primer Tm review before oligo order, multiplex or panel batch QC from CSV, NGS amplicon primer list screening, gradient PCR planning from suggested Ta, and scripted primer validation in CI or LIMS pipelines. Calculator logic runs on Pepkio servers; provide a network connection and API key for `run` commands. Sequences are transmitted to the API for programmatic runs.

# Features

- Single primer pair or batch mode (up to 200 pairs via CSV/TSV or `batch_rows`)
- Polymerase presets: Q5, Phusion, Taq, KAPA HiFi, or custom Na⁺ and Mg²⁺ (mM)
- DMSO (%) correction applied to Tm (−0.675°C per 1%); set `betaine_M` to 0 (betaine returns an error via the API)
- Configurable oligo concentration for Tm (default 250 nM)
- Output: `tm_fwd`, `tm_rev`, `delta_tm`, `ta_suggested`, GC%, hairpin/dimer ΔG, Go/Flag/Fail status
- Method comparison fields (Wallace, GC%, raw SantaLucia, Breslauer) alongside corrected Tm
- Sequence validation: A/C/G/T only (minimum 10 nt); invalid batch rows return row-level errors
- Named manifest examples: `single_q5_pair`, `batch_multiplex`, `invalid_base_row`
- Manifest inspection without an API key

# Quick Start

```bash
docker pull pepkio/tm-annealing-temperature-calculator:0.1.0
docker run --rm -e PEPKIO_API_KEY="your-key" pepkio/tm-annealing-temperature-calculator:0.1.0 \
  pepkio-tm-annealing-temperature-calculator run --example single_q5_pair
```

Manifest only (no API key):

```bash
docker run --rm pepkio/tm-annealing-temperature-calculator:0.1.0 \
  pepkio-tm-annealing-temperature-calculator manifest --examples
```

Set `PEPKIO_API_BASE_URL` to override the API host (default: `https://tools.pepkio.com`). Create an API key with **tools:run** scope at https://www.pepkio.com/account/api-keys.

# Quick Example

```bash
docker run --rm -e PEPKIO_API_KEY="$PEPKIO_API_KEY" pepkio/tm-annealing-temperature-calculator:0.1.0 \
  pepkio-tm-annealing-temperature-calculator run --example batch_multiplex
```

Single pair with custom JSON:

```bash
docker run --rm -e PEPKIO_API_KEY="$PEPKIO_API_KEY" pepkio/tm-annealing-temperature-calculator:0.1.0 \
  pepkio-tm-annealing-temperature-calculator run --input-json \
  '{"mode":"single","name":"test_pair","fwd_seq":"ATGCGTACGTACGTACGTACG","rev_seq":"CGTACGTACGTACGTACGCAT","polymerase_id":"q5","dmso_percent":0,"betaine_M":0}'
```

# Typical Use Cases

- PCR primer pair Tm and Ta before oligo order
- Multiplex or panel primer batch QC from CSV
- NGS amplicon or core-facility primer list review
- GC-rich PCR with DMSO in the master mix
- Gradient PCR planning from suggested Ta and ΔTm
- CI or workflow runners that need a fixed client environment

# Scientific Background

Primary Tm uses SantaLucia 1998 nearest-neighbor thermodynamics with initiation at both 5′ and 3′ termini, then Owczarzy 2008 salt correction (Mg²⁺ and dNTP-aware; von Ahsen Na_eq when Mg=0). DMSO adjusts Tm by −0.675°C per 1%.

Suggested Ta follows polymerase-specific rules: Taq and custom use Tm_lower − 5°C; Q5, Phusion, and KAPA use Tm_lower + 3°C when both primers exceed 20 nt, otherwise Tm_lower (NEB protocols). Hairpin and dimer ΔG use SantaLucia nearest-neighbor at 37°C (alignment-based) as heuristic QC flags.

# Web Application

For researchers who prefer a graphical interface, an interactive web version is available.

Web Application: https://www.pepkio.com/tools/tm-annealing-temperature-calculator

The web UI runs calculations in the browser (sequences are not uploaded during interactive use), supports batch CSV paste or upload, DMSO and betaine adjustments, method comparison panels, sortable results, CSV export, printable worksheets, and shareable links.

# Documentation and Resources

GitHub Repository (source and Dockerfile): https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator

Web Application: https://www.pepkio.com/tools/tm-annealing-temperature-calculator

PyPI package: https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/

# About Pepkio

Pepkio (https://www.pepkio.com/) develops software tools and bioinformatics solutions for life science researchers, including laboratory calculators and analysis services.
