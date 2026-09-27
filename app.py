import argparse
from pathlib import Path

from cleaning import load_and_clean_data
from config import load_config
from excel_report import create_excel_report
from reporting import create_report_data, select_reporting_period


def get_input_file() -> Path:
    """Get the CSV path supplied by the user."""

    parser = argparse.ArgumentParser(
        description="Generate a business report from a CSV file."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file.",
    )

    args = parser.parse_args()
    input_file = Path(args.input)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    if input_file.suffix.lower() != ".csv":
        raise ValueError(
            "Input file must be a CSV file."
        )

    return input_file


if __name__ == "__main__":
    config = load_config()

    input_file = get_input_file()

    # Step 1: Load and clean the user's CSV.
    cleaned_data, cleaning_summary = (
        load_and_clean_data(input_file)
    )

    # Step 2: Select the configured reporting period.
    frequency = config["report"]["frequency"]

    period_data, report_start, report_end = (
        select_reporting_period(
            cleaned_data,
            frequency,
        )
    )

    # Step 3: Create business report calculations.
    report_data = create_report_data(period_data)

    # Step 4: Create the Excel report.
    output_file = Path(config["output_file"])

    if not output_file.is_absolute():
        output_file = (
            Path(__file__).resolve().parent
            / output_file
        )

    revenue_threshold = config["report"][
        "low_revenue_threshold"
    ]

    create_excel_report(
        report_data=report_data,
        cleaning_summary=cleaning_summary,
        report_start=report_start,
        report_end=report_end,
        output_file=output_file,
        revenue_threshold=revenue_threshold,
    )

    print(f"Input CSV: {input_file}")

    print("\nCLEANING SUMMARY")
    print("-----------------")

    for key, value in cleaning_summary.items():
        print(f"{key}: {value}")

    print("\nBUSINESS REPORT")
    print("---------------")

    print(
        f"Reporting Period: "
        f"{report_start:%d %b %Y} - "
        f"{report_end:%d %b %Y}"
    )

    print(
        f"Revenue: "
        f"{report_data['total_revenue']:.2f}"
    )

    print(
        f"Orders: "
        f"{report_data['total_orders']}"
    )

    print(
        f"Units: "
        f"{report_data['total_units']}"
    )

    print(
        f"Average Order Value: "
        f"{report_data['average_order_value']:.2f}"
    )

    print(f"\nExcel report created: {output_file}")