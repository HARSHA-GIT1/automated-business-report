# Automated Business Report Generator

A Python-based automation tool that converts sales CSV data into a structured business report in Excel.

The project automates common reporting tasks such as data cleaning, business metric calculation, pivot-table generation, Excel formatting, and scheduled report generation.

The main goal is to make a recurring business reporting process consistent, repeatable, and less dependent on manual Excel work.

---

## Features

- Accepts a CSV file through the command line
- Validates the input file and required columns
- Removes duplicate records
- Handles missing category values
- Standardizes category names
- Converts numeric fields into usable numeric values
- Recovers missing revenue using units sold and unit price
- Handles multiple date formats
- Removes rows with invalid dates
- Selects the latest reporting period automatically
- Calculates key business metrics
- Generates revenue summaries by region and category
- Generates a top-products report
- Creates pivot tables using Pandas
- Generates a formatted Excel workbook using OpenPyXL
- Applies Excel conditional formatting
- Provides a data-quality summary
- Supports scheduled report generation using APScheduler
- Supports variable-length CSV inputs

---

## How the Project Works

The overall workflow is:

```text
CSV Input
   |
   v
Validate Input
   |
   v
Clean Data
   |
   v
Select Reporting Period
   |
   v
Calculate Business Metrics
   |
   v
Generate Pivot Tables
   |
   v
Create Excel Report
```

The same processing logic can be used with different CSV files without changing the Python code.

---

## Technologies Used

| Technology  | Purpose                                   |
|-------------|--------------------------------------------|
| Python      | Application development                    |
| Pandas      | Data cleaning, transformation and analysis  |
| OpenPyXL    | Excel workbook creation and formatting      |
| APScheduler | Automated scheduled report generation       |
| PyYAML      | Reading project configuration               |

---

## Project Structure

```text
automated-business-report/
│
├── data/
│   ├── input/
│   │   ├── sample_sales.csv
│   │   └── another_sales.csv
│   │
│   └── output/
│       └── weekly_business_report.xlsx
│
├── app.py
├── cleaning.py
├── reporting.py
├── excel_report.py
├── scheduler.py
├── config.py
├── config.yaml
├── generate_sample_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Main files

**app.py**
The main command-line entry point. It accepts the CSV path, runs the processing pipeline, and generates the Excel report.

**cleaning.py**
Loads and cleans the input CSV. It handles duplicates, missing values, numeric conversion, category standardization, and date parsing.

**reporting.py**
Selects the reporting period and calculates business metrics and summary tables.

**excel_report.py**
Creates and formats the final Excel workbook using OpenPyXL.

**scheduler.py**
Runs the report automatically according to the schedule defined in `config.yaml`.

**config.yaml**
Stores input/output paths, report settings, schedule settings, and source-column mappings.

**config.py**
Loads the project configuration from `config.yaml`.

**generate_sample_data.py**
Generates a deliberately messy sample CSV for development and testing.

---

## Setup

### 1. Create a virtual environment

From the project directory:

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

On Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The project's direct dependencies are:

- APScheduler
- openpyxl
- pandas
- PyYAML

---

## Running the Report

The application accepts the input CSV using the `--input` argument.

For example:

```bash
python app.py --input "data\input\sample_sales.csv"
```

You can also provide a different CSV:

```bash
python app.py --input "data\input\another_sales.csv"
```

The application then:

1. Validates the CSV file.
2. Loads the data.
3. Cleans the data.
4. Selects the configured reporting period.
5. Calculates business metrics.
6. Creates summary tables.
7. Generates the Excel report.

---

## Input CSV Format

The default configuration expects these columns:

- Transaction ID
- Order Date
- Product
- Category
- Region
- Units Sold
- Unit Price
- Revenue

For example:

```csv
Transaction ID,Order Date,Product,Category,Region,Units Sold,Unit Price,Revenue
T001,05-12-2026,Laptop,Electronics,South,2,450,900
T002,06-12-2026,Mouse,Accessories,North,5,18,90
```

The actual source column names can be configured in `config.yaml`. This allows the application to map source-specific column names to standard internal field names.

---

## Data Cleaning

The cleaning stage handles common problems found in business data.

**Duplicate records**
Exact duplicate records are removed before reporting.

**Missing categories**
Missing category values are replaced with `Unknown`. Category names are also standardized.

For example:

```
electronics
Electronics
ELECTRONICS
```

are standardized to:

```
Electronics
```

**Missing revenue**
If revenue is missing but units sold and unit price are available, revenue is calculated automatically:

```
Revenue = Units Sold × Unit Price
```

**Numeric conversion**
Fields such as quantity, unit price, and revenue are converted into numeric values so they can be used safely in calculations.

**Date handling**
The application supports different date representations and removes rows where the order date cannot be interpreted as a valid date.

---

## Business Metrics

For the selected reporting period, the application calculates:

**Total Revenue**
The sum of revenue from all valid records.

**Total Orders**
The number of unique transaction IDs.

**Total Units**
The total number of units sold.

**Average Order Value**
Calculated as:

```
Average Order Value = Total Revenue / Total Orders
```

The calculation is protected against division by zero.

---

## Reporting Tables

The report contains summary tables for:

**Revenue by Region**
- Region
- Revenue
- Units
- Orders

**Revenue by Category**
- Category
- Revenue
- Units
- Orders

**Top Products**
Shows the top 10 products based on revenue, including:
- Product
- Revenue
- Units
- Orders

The region and category summaries are generated using Pandas pivot tables.

---

## Excel Report

The final report is saved as an Excel workbook.

The workbook contains two main sheets:

**Executive Summary**
Contains:
- Reporting period
- Total revenue
- Total orders
- Total units
- Average order value
- Revenue by region
- Revenue by category
- Data quality summary

**Top Products**
Contains the top products ranked by revenue.

The workbook also includes:
- Formatted Excel tables
- Number formatting
- Freeze panes
- Hidden gridlines
- Conditional formatting
- Revenue threshold highlighting
- Revenue color-scale formatting

---

## Configuration

Project settings are stored in `config.yaml`.

Example:

```yaml
input_file: data/input/sample_sales.csv
output_file: data/output/weekly_business_report.xlsx

report:
  frequency: weekly
  low_revenue_threshold: 100000
  schedule_day: mon
  schedule_hour: 9
  schedule_minute: 0

columns:
  transaction_id: Transaction ID
  order_date: Order Date
  product: Product
  category: Category
  region: Region
  quantity: Units Sold
  unit_price: Unit Price
  revenue: Revenue

day_first: true
```

Keeping these values in a configuration file means that source column names, report frequency, thresholds, and scheduling settings do not need to be hard-coded throughout the application.

---

## Scheduled Report Generation

The project supports automated report generation using APScheduler.

Start the scheduler with:

```bash
python scheduler.py
```

The scheduler reads the schedule from `config.yaml`.

The current configuration is:

- Day: Monday
- Time: 09:00

The scheduler process must remain running for APScheduler to execute the scheduled job.

### Testing the Scheduler

A test mode is included so the scheduled workflow can be tested without waiting for Monday.

Run:

```bash
python scheduler.py --test
```

The test mode waits a few seconds, generates the report once, and then shuts down automatically.

---

## Example Console Output

After processing a CSV, the application displays a summary similar to:

```text
Input CSV: data\input\another_sales.csv

CLEANING SUMMARY
-----------------
rows_loaded: 5
duplicates_removed: 0
missing_categories_filled: 1
missing_revenue_recovered: 1
invalid_dates_removed: 0
rows_after_cleaning: 5

BUSINESS REPORT
---------------
Reporting Period: 03 Dec 2026 - 09 Dec 2026
Revenue: 505.00
Orders: 5
Units: 15
Average Order Value: 101.00

Excel report created: data\output\weekly_business_report.xlsx
```

---

## Handling Variable-Length Input

The application does not depend on a fixed number of CSV rows.

The same processing logic can handle different input sizes because the calculations and transformations operate on the DataFrame dynamically.

The sample data is only used for development and testing.

Users can provide their own CSV file using:

```bash
python app.py --input "path\to\your\sales.csv"
```

---

## Data Quality Summary

The application reports what happened during the cleaning stage.

For example:

```text
rows_loaded: 506
duplicates_removed: 6
missing_categories_filled: 8
missing_revenue_recovered: 12
invalid_dates_removed: 0
rows_after_cleaning: 500
```

This makes the cleaning process visible instead of silently changing the input data.

---

## Why This Project Was Built

Preparing recurring business reports can involve the same manual steps every week:

1. Open the source data.
2. Clean duplicate and missing records.
3. Fix inconsistent values.
4. Calculate business metrics.
5. Create pivot tables.
6. Format the Excel report.
7. Repeat the process for the next reporting period.

This project automates those steps using Python.

It demonstrates practical skills in:

- Data cleaning
- Data transformation
- Pandas-based analysis
- Pivot-table generation
- Excel automation
- Configuration management
- Command-line applications
- Scheduled automation
- Handling missing and duplicate data
- Working with variable-length input files

---

## Notes

- The files inside `data/input/` are sample/test data.
- The generated Excel reports inside `data/output/` are treated as generated files and are excluded from Git through `.gitignore`.
- The project is intended as a practical demonstration of Python-based business reporting automation and data engineering concepts.
