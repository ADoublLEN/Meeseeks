# 🧩 Meeseeks — Multi-Turn Instruction-Following Benchmark

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](#license)
[![Language](https://img.shields.io/badge/Langs-EN%20%7C%20ZH-informational)](#-quick-start)
[![Category](https://img.shields.io/badge/Benchmark-Instruction--Following-success)](#-key-features)

**Meeseeks** is a benchmark for **multi-turn** instruction following. It evaluates whether models can **self-correct** their responses based on structured feedback—moving beyond single-turn accuracy to measure *adaptability* and *recovery*.

---

## 📌 Contents
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Setup & Requirements](#-setup--requirements)
- [Script Arguments](#-script-arguments)
- [Expected Outputs](#-expected-outputs)
- [Project Layout](#-project-layout)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Cite](#-cite)
- [License](#license)

---

## ✨ Key Features

- **Multi-turn evaluation:** Measures correction behavior across turns with feedback loops.
- **Bilingual pipelines:** Same content for **EN** and **ZH**, with **language-specific evaluation**.
- **Pluggable models:** Bring your own **tested model**, **extraction model**, and **scoring model**.
- **Open or commercial:** Works with open-source (e.g., Qwen) or hosted APIs (e.g., Claude Sonnet).

---

## 🚀 Quick Start

We provide three entry scripts:

```bash
# Run Meeseeks (Chinese)
bash example_run_chinese.sh

# Run Meeseeks (English)
bash example_run_english.sh

# Run Meeseeks on your own dataset
bash example_run_custom.sh
