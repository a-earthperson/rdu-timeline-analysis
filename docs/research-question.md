---
title: Research Question and Scope
---

## Why this analysis exists

Community timeline threads are most useful when they answer a concrete question rather than merely accumulating anecdotes. The motivating question here is:

> For the current public Raleigh/Durham sample, where is the observed delay actually concentrated, and how should an already-interviewed but still-pending case be interpreted?

The repository already publishes the right raw artifacts. What it needed was a reader path. This page defines the question, `key-findings.md` answers it, and `pending-cases.md` explains how to read the open tail without discarding censored cases.

## Current snapshot

As of analysis date `2026-03-15`:

- filtered RDU cases: 47
- closed cases: 29
- pending cases: 18
- receipt years represented: 2023, 2024, 2025
- office filter: `field_office == Raleigh/Durham`

The canonical public dataset lives in `data/canonical/rdu_timeline_data.csv`; the exact filtered input used for the current site build is published at [results/latest/processed/dataset_filtered.csv](results/latest/processed/dataset_filtered.csv).

## What this site can and cannot identify

This is a versioned observational sample, not a population frame. It is useful for describing the current public signal, comparing cohorts, and updating pending-case probabilities under explicit assumptions. It is not a substitute for USCIS administrative data, and it is not legal advice.

The motivating community sample is marriage-based AOS oriented, but the canonical analysis table does not currently encode a formal `case type` variable. That means the site can rigorously analyze observed durations, censoring, and cohort shifts, but it cannot yet stratify the published curves by case subtype without a schema change.

## Analytical frame

The site focuses on two time-to-event questions:

- total time: `I-485 receipt date -> I-485 approval date`
- post-interview lag: `interview date -> I-485 approval date`

Pending rows are not treated as missing. They are right-censored observations at the analysis date and therefore still contribute information about the tail of the distribution. This is why the survival/CDF views and the `pending_predictions.csv` output are central, rather than optional.

## Reading map

Use the pages in this order:

1. [Key Findings](key-findings.md) for the empirical story.
2. [Pending Cases and Forecasts](pending-cases.md) for the current open tail and conditional probabilities.
3. [Methods](methods.md), [Data Contract](data.md), and [Assumptions and Caveats](assumptions.md) for the technical details behind the published curves.
