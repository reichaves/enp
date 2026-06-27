# Data Matching and Audit System — "Escravo, nem pensar!" Project

[![English Version](https://img.shields.io/badge/Language-English-blue.svg)](#)
[![Versão em Português](https://img.shields.io/badge/Linguagem-Português-green.svg)](README.pt-br.md)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-v1.3%2B-darkblue.svg)
![OpenPyXL](https://img.shields.io/badge/OpenPyXL-v3.0%2B-orange.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

This repository contains the Python script ecosystem designed for cleaning, matching (merging), and auditing data related to workers rescued from slave-like conditions in Brazil.

The technical goal of the system is to correlate and consolidate information from three main databases for structured analysis by the **"Escravo, nem pensar!"** project team:
1. **Manual Inspection spreadsheet**: Historical inspection records manually compiled by the initiative's team.
2. **Unemployment Insurance Profile**: Registrations and demographic data of rescued workers who requested unemployment benefits.
3. **Radar SIT**: Official public database of labor inspections maintained by the Undersecretary of Labor Inspection (Subsecretaria de Inspeção do Trabalho).

---

## Author

* **Reinaldo Chaves** (reichaves@gmail.com)
  * GitHub: [@reichaves](https://github.com/reichaves)

---

## Repository Structure

* `.gitignore`: Excludes local configurations, virtual environments, raw datasets, and temporary spreadsheet results from version control.
* `cruzamento_todos_anos.py`: Main ETL script responsible for data cleaning, hierarchical matching, and visual output formatting.
* `auditoria_cruzamento.py`: Post-processing validation tool that verifies physical and temporal data integrity of the generated output.
* `auditoria_residual_2024.py`: Specific audit script analyzing records from 2024 that remained unmatched against Radar SIT, generating diagnostic logs.
* `documentacao.md`: Detailed technical documentation outlining matching logic, data definitions, and maintenance procedures.

> **Note:** The folders `dados_2024_2025/`, `backup/`, and `resultados_scripts/` contain sensitive PII and final spreadsheets. They are restricted from public distribution and excluded via `.gitignore`.

---

## What is ETL?

**ETL** stands for **Extract, Transform, Load**. It is a standardized data engineering pipeline designed to consolidate information from multiple sources:

* **Extract:** Reads raw datasets (`trabalhadores_mai22.xlsx`, `ENP - Perfil do resgatado no Brasil.xlsx`, and `radarsit_mai22.xlsx`) from the `dados_2024_2025/` folder.
* **Transform:** Cleans strings, standardizes document formats (padding CPFs/CNPJs), resolves homonyms via temporal proximity, executes fuzzy matching, and builds hierarchical merges in [cruzamento_todos_anos.py](file:///E:/code/enp/cruzamento_todos_anos.py).
* **Load:** Saves the validated, formatted spreadsheet inside the `resultados_scripts/` folder.

---

## Technical Specifications and ETL Logic

### 1. Pre-processing and Data Cleaning
* **Text Normalization:** Standardizes string formats to uppercase, strips accents (Unicode NFKD normalization), and deletes double or leading/trailing spaces.
* **Document Standardizing:** Removes non-numerical characters from CPF and CNPJ columns, adding leading zeros (*padding*) to guarantee a length of 11 characters for CPFs and 14 for CNPJs.
* **Zero-Collision Prevention:** Converts empty or whitespace-only cells in operation number columns into proper null values (`NaN`), avoiding false links to default "0" identifiers.

### 2. Worker × Unemployment Insurance Matching
The script processes records in a strict hierarchical order:
* **Stage 1:** Exact matching on worker name.
* **Stage 2:** Fuzzy matching using Levenshtein distance (`fuzzywuzzy`) for remaining records, applying a strict cutoff score of 90.
* **Homonym Resolution:** If multiple candidate records exist under the same name, the system calculates the absolute difference in days between the official "Rescue Date" and the "Inspection/Dismissal Date" from manual sheets. Only the record with the minimum temporal difference is kept.
* **Surname Verification:** A verification function checks if the surnames (excluding prepositions) share at least one word. If they share no words, the match is discarded.
* **Temporal Constraint:** Differences in dates exceeding 365 days are flagged as `flag_data_divergente = True`. Unmatched surnames and records exceeding 365 days are excluded.

### 3. Operation × Radar SIT Matching
The integration with Radar SIT is executed under the strict condition of matching fiscal years:
1. **Priority 3 (Highest):** Exact matching on employer document (CNPJ or CPF).
2. **Priority 2:** Exact matching on the cleaned establishment name.
3. **Priority 1 (Lowest):** Cross-matching of manual business/trade names against Radar SIT owner/proprietor names.

Records with no match are kept in the final dataset (via a partial outer join) to prevent data loss, flagged as `flag_estabelecimento = SEM_CORRESPONDENCIA_SIT`.

---

## Installation and Execution

### System Dependencies
* Python $\ge$ 3.8
* pandas
* openpyxl
* fuzzywuzzy
* python-Levenshtein
* matplotlib
* seaborn
* plotly

### Execution

1. **Install dependencies:**
   ```bash
   pip install pandas openpyxl fuzzywuzzy python-Levenshtein matplotlib seaborn plotly
   ```

2. **Run the data matching pipeline:**
   ```bash
   python cruzamento_todos_anos.py
   ```

3. **Validate output integrity:**
   ```bash
   python auditoria_cruzamento.py
   ```

4. **Generate residual audit report (2024 cases):**
   ```bash
   python auditoria_residual_2024.py
   ```

The script `auditoria_cruzamento.py` runs 6 structural tests:
* **Cartesian Product Check:** Checks if duplicate worker records exist for the same manual operation.
* **Homonym Auditor:** Reports totals of unique names vs row counts.
* **"Operation 0" Anomaly:** Checks if incorrect joins occurred with default SIT operation "0".
* **Date Violation Check:** Verifies if records with temporal offsets exceeding 365 days bypassed exclusion.
* **Fiscal Year Consistency:** Ensures no records crossed fiscal years.
* **Establishment Conformance:** Summarizes the frequencies of `flag_estabelecimento` categories (`VALIDADO_POR_CNPJ`, `COMPATIVEL`, `DIVERGENTE`, `AUSENTE`).
