# Distress Radar

A financial distress early-warning dashboard for Indian listed companies, built on the Altman Z-Score model.

Live App: [Coming soon]

## What it does

Distress Radar pulls live financial data for any NSE-listed company and calculates its Altman Z-Score — a five-ratio model widely used in credit analysis and restructuring advisory to assess bankruptcy risk.

Based on the score, companies are placed into one of three zones:

- Safe (Z > 2.99) — low bankruptcy risk
- Grey (1.81 to 2.99) — caution zone, worth monitoring
- Distress (Z < 1.81) — high risk, potential restructuring candidate

## Features

The dashboard fetches live data directly from Yahoo Finance, computes the Z-Score across five financial ratios, and visualises results by zone. Each company can be examined individually, with a full breakdown of how each ratio contributes to its score, along with automated flags highlighting specific risk drivers such as liquidity, leverage, or profitability.

## How the model works

The Altman Z-Score combines five weighted ratios: working capital to total assets (liquidity), retained earnings to total assets (cumulative profitability), EBIT to total assets (operating efficiency), market capitalisation to total liabilities (market value versus debt), and revenue to total assets (asset utilisation).

The model has known limitations. It does not apply well to banks, NBFCs, or asset-light sectors such as IT, where high revenue-to-asset ratios can produce inflated scores. The dashboard accounts for this with visual caps and contextual notes.

## Tech stack

Python, yfinance, Streamlit, Plotly

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Author

Suyogya Swaroop
[LinkedIn](https://www.linkedin.com/in/suyogya-swaroop/)
