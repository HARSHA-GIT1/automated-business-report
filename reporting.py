import pandas as pd


def get_reporting_days(frequency: str) -> int:
    """Convert report frequency into a number of calendar days."""

    frequency = frequency.lower()

    frequency_days = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
    }

    if frequency not in frequency_days:
        raise ValueError(
            f"Unsupported report frequency: {frequency}"
        )

    return frequency_days[frequency]


def select_reporting_period(
    data: pd.DataFrame,
    frequency: str = "weekly",
) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    """Return the latest configured reporting period."""

    days = get_reporting_days(frequency)

    report_end = data["order_date"].max().normalize()

    report_start = (
        report_end
        - pd.Timedelta(days=days - 1)
    )

    period_data = data[
        data["order_date"].between(
            report_start,
            report_end,
        )
    ].copy()

    if period_data.empty:
        raise ValueError(
            "No data found for the latest reporting period."
        )

    return period_data, report_start, report_end


def create_report_data(
    data: pd.DataFrame,
) -> dict:
    """Create the business summaries for the report."""

    total_revenue = data["revenue"].sum()
    total_orders = data["transaction_id"].nunique()
    total_units = data["quantity"].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders
        else 0
    )

    # Pivot table: revenue and units by region.
    revenue_by_region = (
        pd.pivot_table(
            data,
            index="region",
            values=["revenue", "quantity"],
            aggfunc="sum",
        )
        .reset_index()
        .rename(
            columns={
                "revenue": "Revenue",
                "quantity": "Units",
            }
        )
    )

    region_orders = (
        data.groupby("region")["transaction_id"]
        .nunique()
        .rename("Orders")
        .reset_index()
    )

    revenue_by_region = (
        revenue_by_region
        .merge(region_orders, on="region")
        .sort_values(
            "Revenue",
            ascending=False,
        )
    )

    # Pivot table: revenue and units by category.
    revenue_by_category = (
        pd.pivot_table(
            data,
            index="category",
            values=["revenue", "quantity"],
            aggfunc="sum",
        )
        .reset_index()
        .rename(
            columns={
                "revenue": "Revenue",
                "quantity": "Units",
            }
        )
    )

    category_orders = (
        data.groupby("category")["transaction_id"]
        .nunique()
        .rename("Orders")
        .reset_index()
    )

    revenue_by_category = (
        revenue_by_category
        .merge(category_orders, on="category")
        .sort_values(
            "Revenue",
            ascending=False,
        )
    )

    # Top 10 products by revenue.
    top_products = (
        data.groupby("product")
        .agg(
            Revenue=("revenue", "sum"),
            Units=("quantity", "sum"),
            Orders=("transaction_id", "nunique"),
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(10)
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units": total_units,
        "average_order_value": average_order_value,
        "revenue_by_region": revenue_by_region,
        "revenue_by_category": revenue_by_category,
        "top_products": top_products,
    }