# Customer Churn End-to-End Portfolio Project

This project is structured to help you showcase a full data analyst workflow:

1. Data loading from Kaggle dataset
2. EDA, cleaning, and transformations
3. Feature engineering
4. ML model experiments with PyCaret
5. Parquet exports for Power BI
6. Power BI data model + DAX KPI layer
7. Business retention insights
8. SVG background/icon generation for dashboard pages (1920x1080)

## Tech Stack

- Python 3.11 (avoid Python 3.14 for PyCaret compatibility)
- pandas, pyarrow, fastparquet
- PyCaret for classification workflows
- Power BI for dashboarding and DAX measures

## Quick Start

### 1. Create and activate virtual environment (Python 3.11)

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Place raw dataset

Download from Kaggle and place the file(s) under:

- data/raw/

Expected format: CSV or XLSX.

### 3. Run notebook

Open and run:

- notebooks/churn_end_to_end.ipynb

This notebook performs EDA, feature engineering, PyCaret modeling, and parquet exports.

### 4. Load parquet in Power BI

Use files in:

- data/processed/parquet/

Then implement the DAX measures in:

- powerbi/dax/churn_kpis.dax

### 5. Generate dashboard visual assets

Run:

```powershell
python src/assets/generate_powerbi_svgs.py
```

Assets will be saved to:

- powerbi/templates/

## Suggested Power BI Pages

1. Executive Overview
2. Churn Risk Segments
3. Retention Opportunities
4. Model Explainability

See details:

- powerbi/templates/dashboard_pages.md
