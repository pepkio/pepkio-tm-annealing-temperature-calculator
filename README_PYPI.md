# Pepkio Tm / Annealing Temperature Calculator

Python client for the Pepkio Tm / Annealing Temperature Calculator API: primer melting temperature (Tm), suggested annealing temperature (Ta), and QC for single pairs or batch primer lists.

# What It Does

PCR primer design and troubleshooting require consistent Tm and annealing temperature estimates under your buffer, polymerase, and additive conditions. Spreadsheet formulas and generic **Tm − 5 °C** rules often disagree with vendor calculators and do not scale to dozens of primer pairs.

This package calls the same Pepkio Tools calculation engine as the hosted web application. Use `PepkioClient.run()` from Python, Jupyter, or pipelines to obtain per-primer Tm, ΔTm, polymerase-specific suggested Ta, GC%, hairpin and dimer QC flags, and shareable run links.

Programmatic runs require a network connection and a Pepkio API key. Sequences are sent to the API for `run()`; calculations are not bundled for offline use.

# Features

- Single primer pair or batch mode (up to 200 pairs via CSV/TSV or `batch_rows`)
- Polymerase presets: Q5, Phusion, Taq, KAPA HiFi, or custom Na⁺ and Mg²⁺ (mM)
- DMSO (%) and betaine (M) corrections; configurable oligo concentration (default 250 nM)
- Output: `tm_fwd`, `tm_rev`, `delta_tm`, `ta_suggested`, GC%, hairpin/dimer ΔG, Go/Flag/Fail status
- Method comparison fields (Wallace, GC%, raw SantaLucia, Breslauer) alongside corrected Tm
- Manifest and named examples: `get_manifest`, `list_examples`, `get_example_input`
- CLI: `pepkio-tm-annealing-temperature-calculator manifest` and `run`
- Configuration via `PEPKIO_API_KEY` and `PEPKIO_API_BASE_URL`

# Installation

```bash
pip install pepkio-tm-annealing-temperature-calculator
```

Set an API key with **tools:run** scope before calling `run()`:

```bash
export PEPKIO_API_KEY="your-key"
```

Create a key in your [Pepkio account API keys](https://www.pepkio.com/account/api-keys) settings.

# Quick Example

```python
from pepkio_tm_annealing_temperature_calculator import PepkioClient

with PepkioClient() as client:
    inp = client.get_example_input("single_q5_pair")
    result = client.run(inp)
    single = result.result["single"]
    print(single["tm_fwd"], single["tm_rev"], single["ta_suggested"], single["status"])
```

CLI:

```bash
pepkio-tm-annealing-temperature-calculator run --example single_q5_pair
```

Manifest inspection does not require an API key.

# Typical Use Cases

- PCR primer pair Tm and Ta before oligo order
- Multiplex or panel primer batch QC from CSV
- NGS amplicon or core-facility primer list review
- GC-rich PCR with DMSO or betaine in the master mix
- Gradient PCR planning from suggested Ta and ΔTm
- Scripted primer validation in LIMS or bioinformatics workflows

# Scientific Background

**Tm** (melting temperature) estimates duplex stability using SantaLucia 1998 nearest-neighbor thermodynamics with Owczarzy 2004 salt correction (including Mg²⁺ as equivalent monovalent salt). DMSO and betaine adjust Tm when present in the reaction.

**Suggested Ta** is derived from the lower primer Tm minus a polymerase-specific offset, not a single global Tm − 5 °C rule. **ΔTm** between forward and reverse primers indicates primer balance. Hairpin and dimer checks are heuristic QC flags for screening.

# Web Application

For researchers who prefer a graphical interface, an interactive [Tm / Annealing Temperature Calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator) is available in the browser.

The web interface runs calculations locally (sequences are not uploaded during interactive use), supports batch CSV paste or upload, method comparison panels, sortable results, CSV export, printable worksheets, and shareable links. API `permalink` values restore the same run as the web share link.

**Web Application:** [https://www.pepkio.com/tools/tm-annealing-temperature-calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator)

# Documentation and Resources

Full documentation, examples, and issue tracking: [github.com/pepkio/pepkio-tm-annealing-temperature-calculator](https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator)

# About Pepkio

Pepkio develops software tools and provides bioinformatics analysis services for life science research. See https://www.pepkio.com for additional tools and services.

# Keywords

primer Tm calculator, melting temperature calculator, annealing temperature calculator, PCR Tm, PCR annealing temperature, Ta calculator, primer pair Tm, delta Tm, SantaLucia Tm, nearest neighbor Tm, Owczarzy salt correction, Wallace Tm rule, Q5 annealing temperature, Phusion annealing temperature, Taq PCR Tm, DMSO Tm correction, betaine PCR, primer hairpin check, primer dimer QC, batch primer Tm, CSV primer Tm, multiplex PCR primers, oligo Tm calculator, DNA primer thermodynamics, Pepkio, pepkio-tm-annealing-temperature-calculator, Python primer Tm API, how to calculate primer Tm for PCR, what annealing temperature for Q5 PCR, batch Tm calculator multiplex primers, Tm minus 5 vs polymerase Ta offset, correct Tm for DMSO in PCR, primer delta Tm acceptable range, upload CSV primer Tm QC, Python script primer melting temperature API, Pepkio Tm annealing temperature calculator web, shareable PCR primer calculation link, primer Tm without browser upload, NGS amplicon primer Tm batch, core facility primer order Tm check
