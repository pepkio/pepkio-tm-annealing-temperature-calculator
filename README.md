# Pepkio Tm / Annealing Temperature Calculator

Python client for the Pepkio Tm / Annealing Temperature Calculator API: primer melting temperature (Tm), suggested annealing temperature (Ta), and QC for single primer pairs or batch runs.

# Overview

PCR and other primer-extension assays depend on choosing an **annealing temperature** (Ta) that allows specific binding without nonspecific amplification. **Melting temperature** (Tm) estimates how stable a primer duplex is under defined salt, magnesium, oligo concentration, and additive conditions. For a primer pair, the limiting primer is usually the one with lower Tm; **ΔTm** between forward and reverse primers indicates how balanced the pair is.

Researchers routinely estimate Tm with vendor calculators, Wallace rules, or spreadsheet formulas. Those approaches often disagree because they use different thermodynamic tables, salt corrections, or additive models. A fixed rule such as **Tm − 5 °C** for Ta does not match manufacturer recommendations for high-fidelity enzymes (for example Q5 or Phusion), and batch primer lists are tedious to process one row at a time.

The [Pepkio Tm / Annealing Temperature Calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator) computes primer Tm with **SantaLucia 1998** nearest-neighbor thermodynamics, **Owczarzy 2004** monovalent salt correction, and adjustments for DMSO and betaine. It returns a **polymerase-specific suggested Ta**, GC content, hairpin and dimer QC flags, and optional method comparison values (Wallace, GC%, Breslauer) so you can see why another calculator reported a different number.

This repository provides the **Python client** (`pepkio-tm-annealing-temperature-calculator`) that calls the same calculation engine through the Pepkio Tools REST API for scripts, notebooks, LIMS hooks, and automated primer QC pipelines.

For an interactive interface with in-browser calculation (sequences stay on your machine), use the hosted tool at [https://www.pepkio.com/tools/tm-annealing-temperature-calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator). For reproducible programmatic access, install the package from [PyPI](https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/) and follow Quick Start below.

# Features

## Tm and Ta calculation (API-backed)

- **Single primer pair mode:** forward and optional reverse sequence, pair name, polymerase preset
- **Batch mode:** up to **200** primer pairs via pasted CSV/TSV (`name,fwd,rev`) or structured `batch_rows`
- **Polymerase presets:** Q5, Phusion, Taq, KAPA HiFi, or **custom** Na⁺ and Mg²⁺ (mM)
- **Reaction additives:** DMSO (%) and betaine (M) corrections applied to Tm
- **Oligo concentration:** configurable nM for Tm (default 250 nM)
- **Per-primer output:** `tm_fwd`, `tm_rev`, `delta_tm`, `ta_suggested`, GC%, hairpin ΔG, dimer ΔG
- **QC status:** Go / Flag / Fail with `qc_reasons` (for example unbalanced Tm, hairpin, dimer)
- **Method comparison:** Wallace rule, GC%-based estimate, raw SantaLucia and Breslauer values alongside corrected Tm
- **Sequence validation:** DNA bases A/C/G/T only; invalid rows return row-level errors in batch mode
- **Shareable runs:** each API run returns a `permalink` that restores inputs and results

## Python package

- Fetch the tool manifest and list named examples (`get_manifest`, `list_examples`, `get_example_input`)
- Run calculations synchronously (`run`) with custom JSON or manifest examples
- Poll runs if needed (`get_run`, `wait_for_run`)
- CLI for manifest inspection and one-off runs (`pepkio-tm-annealing-temperature-calculator`)
- Configurable API base URL and API keys via environment variables

# Common Use Cases

### Standard PCR primer pair before ordering (`single_q5_pair`)

Check Tm and suggested Ta for a new forward/reverse pair using the Q5 buffer preset, confirm ΔTm is small, and review hairpin or dimer flags before placing an oligo order.

### Multiplex or panel primer QC (`batch_multiplex`)

Paste or upload a CSV of many primer pairs (for example housekeeping genes in a multiplex panel), sort results by status, and export flagged rows for redesign.

### GC-rich or additive PCR (`single` with DMSO or betaine)

Include DMSO or betaine in the input when your master mix contains these additives so Tm and Ta reflect bench conditions rather than a salt-only model.

### Core facility or bioinformatics review

Run batch QC on primer lists submitted with NGS amplicon designs, CRISPR guides, or custom panel orders; share a permalink with the submitter.

### Gradient PCR planning

Use suggested Ta and ΔTm to set a temperature gradient range when optimizing a new primer set on a thermal cycler.

# Why This Tool Exists

Spreadsheets and one-size-fits-all **Tm − 5 °C** rules do not account for enzyme-specific Ta offsets, magnesium-dependent salt equivalence, or DMSO and betaine in the reaction mix.

Vendor Tm calculators are reliable for their own enzymes but may not support batch upload, custom salt, or the same thermodynamic path as your in-house scripts.

Tools that analyze hairpins or dimers in depth often handle **one primer at a time** and may require uploading sequences to a remote server.

The Pepkio Tm / Annealing Temperature Calculator combines **batch Tm and Ta** for common polymerase presets (or custom salt), **additive corrections**, **per-pair QC flags**, and a **method comparison** panel in one workflow. The web console runs calculations in the browser so sequences are not transmitted for interactive use. The Python package in this repository calls the hosted API for scripted workflows (see FAQ on data handling).

# Installation

Install from PyPI:

```bash
pip install pepkio-tm-annealing-temperature-calculator
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pepkio-tm-annealing-temperature-calculator
```

PyPI package: [https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/](https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/)

## API key

Programmatic runs require a Pepkio API key with **tools:run** scope. Create one at [https://www.pepkio.com/account/api-keys](https://www.pepkio.com/account/api-keys).

```bash
export PEPKIO_API_KEY="your-key"
```

| Variable | Description |
|----------|-------------|
| `PEPKIO_API_KEY` | Production (or default) API key |
| `LOCAL_PEPKIO_API_KEY` | Local dev key when base URL points to `tools.localtest.me` |
| `PEPKIO_API_BASE_URL` | Override API host (default: `https://tools.pepkio.com`) |
| `PEPKIO_SSL_VERIFY` | Set to `0` or `false` to disable TLS verify (local dev disables verify for `localtest.me` by default) |

Local development against a staging stack:

```bash
export PEPKIO_API_BASE_URL=https://tools.localtest.me
export PEPKIO_API_KEY="$LOCAL_PEPKIO_API_KEY"
```

Web UI (local): [https://www.localtest.me/tools/tm-annealing-temperature-calculator](https://www.localtest.me/tools/tm-annealing-temperature-calculator)

# Quick Start

Manifest inspection does **not** require an API key. Running the tool does.

### Python: manifest example

```python
from pepkio_tm_annealing_temperature_calculator import PepkioClient

with PepkioClient() as client:
    inp = client.get_example_input("single_q5_pair")
    result = client.run(inp)
    single = result.result["single"]
    print(result.status, result.permalink)
    print("Tm fwd:", single["tm_fwd"], "Tm rev:", single["tm_rev"])
    print("Suggested Ta:", single["ta_suggested"], "Status:", single["status"])
```

### Python: custom single pair (Q5)

```python
from pepkio_tm_annealing_temperature_calculator import PepkioClient

inp = {
    "mode": "single",
    "name": "my_amplicon",
    "fwd_seq": "ATGCGTACGTACGTACGTACG",
    "rev_seq": "CGTACGTACGTACGTACGCAT",
    "polymerase_id": "q5",
    "dmso_percent": 0,
    "betaine_M": 0,
    "oligo_concentration_nM": 250,
}

with PepkioClient() as client:
    result = client.run(inp)
    assert result.status == "completed"
```

### Python: batch from CSV text

```python
from pepkio_tm_annealing_temperature_calculator import PepkioClient

inp = {
    "mode": "batch",
    "polymerase_id": "taq",
    "batch_csv": (
        "name,fwd,rev\n"
        "GAPDH_F,GAAGGTGAAGGTCGGAGTC,GAAGATGGTGATGGGATTTC\n"
        "ACTB_F,GGCTGGGGTGTTGAAGGT,CCGCTCGTTGTAGACAGG\n"
    ),
}

with PepkioClient() as client:
    result = client.run(inp)
    for row in result.result["batch"]:
        print(row.get("name"), row.get("tm_fwd"), row.get("ta_suggested"), row.get("status"))
```

### CLI

```bash
pepkio-tm-annealing-temperature-calculator manifest --examples
pepkio-tm-annealing-temperature-calculator run --example single_q5_pair
```

With custom JSON:

```bash
pepkio-tm-annealing-temperature-calculator run --input-json '{"mode":"single","fwd_seq":"ATGCATGCATGC","rev_seq":"GCATGCATGCAT","polymerase_id":"phusion"}'
```

# Example Output

Representative JSON from a completed single-pair run (Q5 preset, example `single_q5_pair`):

```json
{
  "run_id": "12d7a8a9-0d74-4237-8763-d89cea29f1f6",
  "status": "completed",
  "result": {
    "mode": "single",
    "polymerase_id": "q5",
    "method_used": "santaLucia1998",
    "metadata": {
      "na_mM": 50,
      "mg_mM": 2,
      "oligo_concentration_nM": 250,
      "ta_offset_c": 1
    },
    "corrections_applied": {
      "salt_owczarzy": true,
      "dmso": false,
      "betaine": false
    },
    "single": {
      "name": "test_pair",
      "tm_fwd": 67.1,
      "tm_rev": 67.1,
      "delta_tm": 0,
      "ta_suggested": 66.1,
      "gc_fwd": 52.4,
      "gc_rev": 52.4,
      "hairpin_dg_fwd": -16.78,
      "dimer_dg": -0.5,
      "status": "flag",
      "qc_reasons": ["Hairpin ΔG forward -16.78 kcal/mol < -2"],
      "method_comparison_fwd": {
        "wallace_c": 64,
        "gc_percent_c": 57.8,
        "santa_lucia_raw_c": 72.7,
        "breslauer_raw_c": 89.2
      }
    }
  },
  "permalink": "https://tools.pepkio.com/r/12d7a8a9-0d74-4237-8763-d89cea29f1f6"
}
```

Suggested Ta (66.1 °C) is derived from the lower primer Tm minus the Q5-specific offset (1 °C in metadata), not from a generic Tm − 5 °C rule. Status `flag` indicates QC review is recommended; `go` and `fail` are also returned depending on thresholds.

# Scientific Background

## Melting temperature (Tm)

Tm is the temperature at which half of the primer molecules are hybridized in equilibrium under stated conditions. Accurate Tm depends on sequence composition (nearest-neighbor stacking), strand concentration, and ionic environment.

## SantaLucia 1998 nearest-neighbor model

The primary Tm calculation uses **SantaLucia 1998** thermodynamic parameters with initiation contributions at both the 5′ and 3′ termini. This nearest-neighbor (NN) approach sums stacking enthalpy and entropy terms along the primer rather than using a single GC% formula.

## Salt correction (Owczarzy 2004)

Raw NN Tm is referenced to 1 M Na⁺. The engine applies **Owczarzy 2004** monovalent salt correction to match your buffer. For polymerase presets, magnesium is converted to an equivalent monovalent concentration:

**Na_eq (mM) = Na⁺ + 120 × √(Mg²⁺)**

(dNTP correction is not applied in this tool.)

## DMSO and betaine

- **DMSO:** −0.675 °C per 1% DMSO
- **Betaine:** empirical −0.75 °C per 1 M betaine

Enter the values present in your PCR master mix so corrected Tm reflects bench conditions.

## Suggested annealing temperature (Ta)

A common laboratory shortcut is **Ta ≈ Tm − 5 °C**. Pepkio instead computes:

**Ta_suggested = min(Tm_fwd, Tm_rev) − polymerase_offset**

Offsets are polymerase-specific (for example Q5 uses a 1 °C offset from the lower Tm). This aligns Ta with enzyme manufacturer guidance more closely than a single global rule.

## ΔTm and primer balance

**ΔTm = |Tm_fwd − Tm_rev|**. Large ΔTm can cause one primer to anneal preferentially, reducing efficiency or increasing mispriming. Many workflows target ΔTm below about 2–5 °C depending on assay stringency.

## Alternative Tm estimates (method comparison)

The output may include simplified estimates for comparison:

- **Wallace rule:** Tm ≈ 2 °C × (A+T) + 4 °C × (G+C) for short oligos
- **GC%-based** empirical formulas
- **Breslauer** and **raw SantaLucia** values before salt and additive corrections

Differences between vendor calculators often arise from which model, salt correction, and concentration assumptions are used—not from arithmetic error alone.

## Hairpin and dimer QC

Hairpin and homo-/hetero-dimer stabilities are reported as heuristic **ΔG** estimates for QC flags. They are useful for screening but are **not** full thermodynamic folding simulations. Treat Flag/Fail statuses as prompts to redesign or test empirically.

## Valid sequences

Only **A, C, G, T** (uppercase or lowercase) are accepted. Ambiguous IUPAC codes and RNA (U) are rejected with row-level errors in batch mode.

# Frequently Asked Questions

### What is primer Tm (melting temperature)?

Tm is the temperature at which half of a primer is duplexed under defined salt, magnesium, primer concentration, and additive conditions. It guides PCR annealing temperature selection.

### What is PCR annealing temperature (Ta)?

Ta is the temperature step in PCR during which primers bind template. It is usually set below Tm to balance specificity and yield. Pepkio suggests Ta from the lower primer Tm minus a polymerase-specific offset.

### Why do different Tm calculators give different results?

Calculators may use Wallace rules, older NN tables, different salt or Mg²⁺ models, different oligo concentrations, or no DMSO/betaine correction. The method comparison fields in Pepkio output help explain gaps versus Wallace, GC%, or raw NN values.

### What is the Tm minus 5 rule?

Ta ≈ Tm − 5 °C is a historical rule of thumb. High-fidelity polymerases often recommend smaller offsets. Pepkio uses enzyme-specific offsets instead of a single global subtraction.

### How do I calculate Tm for a primer pair?

Enter forward and reverse sequences, select polymerase (or custom salt), and optional DMSO and betaine. The tool returns Tm per primer, ΔTm, and suggested Ta. Use the [web calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator) or the Python client Quick Start above.

### Which polymerases are supported?

Presets include **Q5**, **Phusion**, **Taq**, and **KAPA HiFi**, each with defined Na⁺ and Mg²⁺. Choose **custom** to set `custom_na_mM` and `custom_mg_mM` manually.

### How does DMSO affect primer Tm?

DMSO destabilizes duplexes and lowers Tm. This tool applies −0.675 °C per 1% DMSO. Enter the DMSO percentage in your reaction when estimating Ta.

### How does betaine affect primer Tm?

Betaine can stabilize amplification in GC-rich templates; the tool applies an empirical −0.75 °C per 1 M betaine to Tm. Enter betaine concentration in molar units.

### What oligo concentration is used for Tm?

Default **250 nM** per primer (`oligo_concentration_nM`). Change it if your effective primer concentration in the reaction differs.

### What is ΔTm and why does it matter?

ΔTm is the absolute difference between forward and reverse primer Tm values. Large ΔTm can cause uneven annealing; many labs prefer ΔTm under a few degrees for routine PCR.

### How do I run batch Tm for many primers?

Set `mode` to `batch` and supply `batch_csv` (columns `name,fwd,rev`) or `batch_rows`. Up to **200** pairs per run. See the `batch_multiplex` manifest example.

### What do Go, Flag, and Fail mean?

QC statuses summarize primer pair suitability: **go** passes default thresholds; **flag** recommends review (for example strong hairpin or high ΔTm); **fail** indicates a serious issue. Read `qc_reasons` for detail.

### Are hairpin and dimer checks quantitative?

They use heuristic ΔG estimates for screening, not full secondary-structure prediction. Empirical PCR remains the final test.

### Can I compare Wallace or GC% Tm to SantaLucia?

Yes. Single-mode output includes `method_comparison_fwd` and `method_comparison_rev` with Wallace, GC%-based, raw SantaLucia, and Breslauer estimates alongside corrected Tm.

### Do I need an API key for the Python client?

No key is required for `get_manifest()` or the CLI `manifest` command. `run()` and the CLI `run` command require an API key with tools:run scope.

### Does the Python client send my sequences to a server?

Yes. API runs POST sequences to the Pepkio Tools service. The **web console** performs interactive calculations in the browser without uploading sequences. Choose the interface that matches your data-handling requirements.

### Can I run the tool offline?

The Python package requires network access and a valid API key for runs. Calculations are not bundled for fully offline use in this package. The web UI can compute offline in the browser once loaded.

### How do I share results with a colleague?

Use the `permalink` from an API run or the shareable link in the web tool to restore the same inputs and results.

### What sequences are invalid?

Only A, C, G, and T are accepted. Invalid characters (for example X, N, or U) return errors; batch mode reports them per row.

### How is suggested Ta different from Tm?

Tm describes duplex stability. Ta is the recommended PCR annealing step temperature, computed from the lower primer Tm minus a polymerase-specific offset, after salt and additive corrections.

### Is this the same as NEB Tm Calculator or IDT OligoAnalyzer?

NEB and IDT tools are widely used for single-primer or vendor-specific workflows. Pepkio Tm / Annealing Temperature Calculator emphasizes **batch pairs**, **polymerase-specific Ta**, **DMSO/betaine**, **QC flags**, and **cross-method comparison** in one table, with optional API automation via this package.

# Web Application

For interactive primer Tm and Ta without writing code, open the Pepkio Tm / Annealing Temperature Calculator in your browser.

The web version provides an interactive interface, live validation as you type, batch CSV paste or upload (up to 200 pairs), sortable results, a method comparison panel (Wallace, GC%, raw NN models versus corrected Tm), export to CSV, copy to clipboard, printable worksheets, and shareable links. Calculations run locally in the browser, so primer sequences are not uploaded during normal interactive use.

The web UI also supports:

- **Polymerase presets** — Q5, Phusion, Taq, KAPA HiFi, or custom Na⁺/Mg²⁺
- **Additive fields** — DMSO (%) and betaine (M)
- **Per-pair QC** — Go / Flag / Fail with hairpin, dimer, and ΔTm reasons
- **Batch table** — multiplex and panel primer review in one view
- **Method comparison** — explain differences versus other calculators

**Web Application:** [https://www.pepkio.com/tools/tm-annealing-temperature-calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator)

# Related Resources

- **GitHub Repository:** [https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator](https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator)
- **PyPI Package:** [https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/](https://pypi.org/project/pepkio-tm-annealing-temperature-calculator/)
- **Web Application:** [https://www.pepkio.com/tools/tm-annealing-temperature-calculator](https://www.pepkio.com/tools/tm-annealing-temperature-calculator)

# About Pepkio

[Pepkio](https://www.pepkio.com) develops software tools and bioinformatics solutions for life science researchers, including laboratory calculators and analysis services (RNA-seq, single-cell RNA-seq, spatial transcriptomics, functional enrichment, and custom workflows).

# Citation

If you use Pepkio Tm / Annealing Temperature Calculator in a publication or protocol, cite the web tool and optionally the Python package version:

```bibtex
@misc{pepkio_tm_annealing_temperature_calculator,
  title        = {Pepkio Tm / Annealing Temperature Calculator},
  author       = {Pepkio},
  year         = {2026},
  howpublished = {\url{https://www.pepkio.com/tools/tm-annealing-temperature-calculator}},
  note         = {Python client: pepkio-tm-annealing-temperature-calculator on PyPI}
}
```

# License

See the [GitHub repository](https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator) for license terms.

# Keywords

primer Tm calculator, melting temperature calculator, annealing temperature calculator, PCR Tm, PCR annealing temperature, Ta calculator, primer pair Tm, delta Tm, primer Tm difference, SantaLucia Tm, nearest neighbor Tm, Owczarzy salt correction, Wallace Tm rule, Breslauer Tm, GC percent primer, Q5 annealing temperature, Phusion annealing temperature, Taq PCR temperature, KAPA HiFi Tm, DMSO Tm correction, betaine PCR Tm, primer hairpin check, primer dimer check, multiplex PCR primer design, batch primer Tm, CSV primer Tm, oligo Tm calculator, DNA primer thermodynamics, PCR primer QC, gradient PCR planning, NGS amplicon primer, CRISPR primer Tm, molecular biology calculator, Pepkio, pepkio-tm-annealing-temperature-calculator, Python primer Tm API, lab primer validation, custom PCR buffer Tm, magnesium salt Tm correction, monovalent salt Tm, oligo concentration Tm, forward reverse primer balance, primer redesign flags, method comparison Tm, high fidelity polymerase Ta, GC rich PCR primer, proprietary primer local calculation

how to calculate primer melting temperature for PCR, what annealing temperature should I use for Q5 PCR, why do NEB and IDT Tm calculators disagree, Tm minus 5 rule vs polymerase specific Ta, how to correct Tm for DMSO in PCR, betaine effect on primer annealing temperature, batch Tm calculator for multiplex primers, upload CSV primer Tm QC, primer hairpin delta G threshold PCR, primer dimer QC before ordering oligos, calculate Tm for forward and reverse primers, SantaLucia 1998 vs Wallace Tm for short primers, Owczarzy salt correction explained PCR, equivalent sodium from magnesium PCR buffer, how much delta Tm is acceptable for PCR, suggested Ta from lower primer Tm, Phusion HF annealing temp calculator, Taq polymerase primer Tm preset, custom Na and Mg Tm calculator, 250 nM primer concentration Tm default, flag fail primer QC reasons, export primer Tm table CSV lab notebook, shareable PCR primer calculation link, Python script primer Tm API, primer Tm without uploading sequences browser, review 200 primer pairs Tm at once, core facility primer order Tm check, NGS panel primer Tm batch validation, gradient PCR temperature range from Tm, invalid DNA base primer error ACGT only, compare Wallace GC Breslauer Tm same primer, Pepkio Tm annealing temperature calculator web tool, programmatic primer Tm REST API life science

# Contributing

Clone [https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator](https://github.com/pepkio/pepkio-tm-annealing-temperature-calculator), run `uv sync`, and execute `uv run pytest` for unit and integration tests. Integration tests require `PEPKIO_API_KEY` or `LOCAL_PEPKIO_API_KEY` in the environment.
