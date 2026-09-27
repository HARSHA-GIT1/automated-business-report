from pathlib import Path

import pandas as pd

from config import load_config


PROJECT_ROOT = Path(__file__).resolve().parent


def load_and_clean_data(
    input_file: Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Load the CSV and clean it for business reporting."""

    config = load_config()
    columns = config["columns"]

    # Use the user-provided CSV when available.
    # Otherwise, use the CSV configured in config.yaml.
    if input_file is None:
        input_file = PROJECT_ROOT / config["input_file"]
    else:
        input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    data = pd.read_csv(input_file)

    if data.empty:
        raise ValueError("Input CSV is empty.")

    required_fields = [
        "transaction_id",
        "order_date",
        "product",
        "category",
        "region",
        "quantity",
        "revenue",
    ]

    missing_columns = [
        columns[field]
        for field in required_fields
        if columns[field] not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Rename user-defined columns to standard internal names.
    data = data.rename(
        columns={
            source: field
            for field, source in columns.items()
        }
    ).copy()

    summary = {
        "rows_loaded": len(data),
        "duplicates_removed": 0,
        "missing_categories_filled": 0,
        "missing_revenue_recovered": 0,
        "invalid_dates_removed": 0,
        "rows_after_cleaning": 0,
    }

    # Remove exact duplicate records.
    duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates()
    summary["duplicates_removed"] = duplicates

    # Clean text fields and standardize category names.
    for column in ["product", "category", "region"]:
        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
        )

    missing_categories = int(
        data["category"].isna().sum()
    )

    data["category"] = (
        data["category"]
        .str.lower()
        .str.title()
        .fillna("Unknown")
    )

    summary["missing_categories_filled"] = (
        missing_categories
    )

    # Convert numeric fields.
    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce",
    )

    data["unit_price"] = pd.to_numeric(
        data["unit_price"],
        errors="coerce",
    )

    data["revenue"] = pd.to_numeric(
        data["revenue"],
        errors="coerce",
    )

    # Recover revenue when quantity and price are available.
    recoverable = (
        data["revenue"].isna()
        & data["quantity"].notna()
        & data["unit_price"].notna()
    )

    data.loc[recoverable, "revenue"] = (
        data.loc[recoverable, "quantity"]
        * data.loc[recoverable, "unit_price"]
    )

    summary["missing_revenue_recovered"] = int(
        recoverable.sum()
    )

    # Parse dates.
    # First handle ISO dates such as 2026-12-05.
    raw_dates = data["order_date"].astype("string").str.strip()

    iso_dates = pd.to_datetime(
        raw_dates,
        format="%Y-%m-%d",
        errors="coerce",
    )

    # Parse remaining dates using the configured day-first setting.
    remaining_dates = pd.to_datetime(
        raw_dates.where(iso_dates.isna()),
        format="mixed",
        dayfirst=config.get("day_first", True),
        errors="coerce",
    )

    data["order_date"] = iso_dates.fillna(remaining_dates)

    invalid_dates = int(
        data["order_date"].isna().sum()
    )

    data = data.dropna(
        subset=["order_date"]
    )

    summary["invalid_dates_removed"] = invalid_dates

    # Quantity and revenue are required for calculations.
    data = data.dropna(
        subset=["quantity", "revenue"]
    )

    data["order_date"] = (
        data["order_date"].dt.normalize()
    )

    summary["rows_after_cleaning"] = len(data)

    return data, summary


if __name__ == "__main__":
    cleaned_data, summary = load_and_clean_data()

    print("CLEANING SUMMARY")
    print("-----------------")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nCLEANED DATA SAMPLE")
    print("-------------------")
    print(cleaned_data.head())