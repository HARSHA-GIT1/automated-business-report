from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


OUTPUT_FILE = Path("data/input/sample_sales.csv")


PRODUCTS = {
    "Electronics": [
        ("Wireless Mouse", 18.99),
        ("Keyboard", 29.99),
        ("USB-C Hub", 34.50),
        ("Webcam", 49.99),
    ],
    "Furniture": [
        ("Office Chair", 149.99),
        ("Desk Lamp", 39.99),
        ("Standing Desk", 299.00),
        ("Bookshelf", 119.50),
    ],
    "Office Supplies": [
        ("Notebook", 6.99),
        ("Printer Paper", 8.49),
        ("Stapler", 12.75),
        ("Marker Set", 9.99),
    ],
}


def create_sample_data() -> None:
    """Create a small, deliberately messy sales dataset."""
    random.seed(42)

    rows = []
    start_date = datetime(2026, 8, 1)

    category_variants = {
        "Electronics": [
            "Electronics",
            "electronics",
            "ELECTRONICS",
        ],
        "Furniture": [
            "Furniture",
            "furniture",
            "FURNITURE",
        ],
        "Office Supplies": [
            "Office Supplies",
            "office supplies",
            "OFFICE SUPPLIES",
        ],
    }

    for number in range(1, 501):
        category = random.choice(
            list(PRODUCTS)
        )
        product, unit_price = random.choice(
            PRODUCTS[category]
        )

        quantity = random.randint(1, 8)
        order_date = (
            start_date
            + timedelta(
                days=random.randint(0, 60)
            )
        )

        date_style = random.choice(
            ["iso", "day_first", "text"]
        )

        if date_style == "iso":
            formatted_date = order_date.strftime(
                "%Y-%m-%d"
            )

        elif date_style == "day_first":
            # Use days 13-28 so DD/MM/YYYY is not ambiguous.
            safe_date = order_date.replace(
                day=random.randint(13, 28)
            )
            formatted_date = safe_date.strftime(
                "%d/%m/%Y"
            )

        else:
            formatted_date = order_date.strftime(
                "%b %d, %Y"
            )

        rows.append(
            {
                "Transaction ID": f"T{number:05d}",
                "Order Date": formatted_date,
                "Product": product,
                "Category": random.choice(
                    category_variants[category]
                ),
                "Region": random.choice(
                    ["North", "South", "East", "West"]
                ),
                "Units Sold": quantity,
                "Unit Price": unit_price,
                "Revenue": round(
                    quantity * unit_price,
                    2,
                ),
            }
        )

    data = pd.DataFrame(rows)

    # Deliberately introduce missing values.
    data.loc[
        random.sample(range(len(data)), 8),
        "Category",
    ] = pd.NA

    data.loc[
        random.sample(range(len(data)), 12),
        "Revenue",
    ] = pd.NA

    # Deliberately introduce duplicate records.
    duplicates = data.sample(
        6,
        random_state=42,
    )

    data = pd.concat(
        [data, duplicates],
        ignore_index=True,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Created: {OUTPUT_FILE}")
    print(f"Rows: {len(data)}")


if __name__ == "__main__":
    create_sample_data()