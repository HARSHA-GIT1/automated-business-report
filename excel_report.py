from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


BLUE = "2563EB"
NAVY = "1F4E79"
LIGHT_BLUE = "DBEAFE"
WHITE = "FFFFFF"
RED = "FECACA"


def write_table(
    sheet,
    dataframe,
    start_row,
    table_name,
    threshold,
    color_scale=False,
):
    """Write a DataFrame as a formatted Excel table."""

    for column, name in enumerate(dataframe.columns, 1):
        cell = sheet.cell(
            row=start_row,
            column=column,
            value=name,
        )
        cell.font = Font(
            bold=True,
            color=WHITE,
        )
        cell.fill = PatternFill(
            "solid",
            fgColor=BLUE,
        )
        cell.alignment = Alignment(
            horizontal="center",
        )

    for row, values in enumerate(
        dataframe.itertuples(index=False),
        start_row + 1,
    ):
        for column, value in enumerate(values, 1):
            cell = sheet.cell(
                row=row,
                column=column,
                value=value,
            )

            if dataframe.columns[column - 1] == "Revenue":
                cell.number_format = "0.00"

    if dataframe.empty:
        return

    end_row = start_row + len(dataframe)
    end_column = len(dataframe.columns)
    end_letter = sheet.cell(
        row=start_row,
        column=end_column,
    ).column_letter

    table = Table(
        displayName=table_name,
        ref=f"A{start_row}:{end_letter}{end_row}",
    )

    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showRowStripes=True,
    )

    sheet.add_table(table)

    if "Revenue" not in dataframe.columns:
        return

    revenue_column = (
        dataframe.columns.get_loc("Revenue") + 1
    )

    revenue_letter = sheet.cell(
        row=start_row,
        column=revenue_column,
    ).column_letter

    revenue_range = (
        f"{revenue_letter}{start_row + 1}:"
        f"{revenue_letter}{end_row}"
    )

    sheet.conditional_formatting.add(
        revenue_range,
        CellIsRule(
            operator="lessThan",
            formula=[str(threshold)],
            fill=PatternFill(
                "solid",
                fgColor=RED,
            ),
        ),
    )

    if color_scale:
        sheet.conditional_formatting.add(
            revenue_range,
            ColorScaleRule(
                start_type="min",
                start_color="FEE2E2",
                mid_type="percentile",
                mid_value=50,
                mid_color="FEF3C7",
                end_type="max",
                end_color="DCFCE7",
            ),
        )


def create_excel_report(
    report_data,
    cleaning_summary,
    report_start,
    report_end,
    output_file: Path,
    revenue_threshold,
):
    """Create the weekly Excel business report."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook = Workbook()
    summary = workbook.active
    summary.title = "Executive Summary"

    products = workbook.create_sheet(
        "Top Products"
    )

    # Executive Summary
    summary["A1"] = "WEEKLY BUSINESS REPORT"
    summary["A1"].font = Font(
        size=16,
        bold=True,
        color=WHITE,
    )
    summary["A1"].fill = PatternFill(
        "solid",
        fgColor=NAVY,
    )
    summary.merge_cells("A1:D1")

    summary["A2"] = (
        f"{report_start:%d %b %Y} - "
        f"{report_end:%d %b %Y}"
    )

    kpis = [
        ("Total Revenue", report_data["total_revenue"]),
        ("Total Orders", report_data["total_orders"]),
        ("Total Units", report_data["total_units"]),
        (
            "Average Order Value",
            report_data["average_order_value"],
        ),
    ]

    for column, (label, value) in enumerate(kpis, 1):
        header = summary.cell(
            row=4,
            column=column,
            value=label,
        )
        result = summary.cell(
            row=5,
            column=column,
            value=value,
        )

        header.font = Font(
            bold=True,
            color=WHITE,
        )
        header.fill = PatternFill(
            "solid",
            fgColor=BLUE,
        )
        header.alignment = Alignment(
            horizontal="center",
        )

        result.font = Font(
            size=13,
            bold=True,
            color=NAVY,
        )
        result.fill = PatternFill(
            "solid",
            fgColor=LIGHT_BLUE,
        )
        result.alignment = Alignment(
            horizontal="center",
        )

        if label in [
            "Total Revenue",
            "Average Order Value",
        ]:
            result.number_format = "0.00"

    summary["A8"] = "REVENUE BY REGION"
    summary["A8"].font = Font(
        bold=True,
        color=NAVY,
    )

    write_table(
        summary,
        report_data["revenue_by_region"],
        9,
        "RegionTable",
        revenue_threshold,
    )

    category_row = (
        12
        + len(report_data["revenue_by_region"])
    )

    summary.cell(
        row=category_row,
        column=1,
        value="REVENUE BY CATEGORY",
    ).font = Font(
        bold=True,
        color=NAVY,
    )

    write_table(
        summary,
        report_data["revenue_by_category"],
        category_row + 1,
        "CategoryTable",
        revenue_threshold,
    )

    quality_row = (
        category_row
        + len(report_data["revenue_by_category"])
        + 4
    )

    summary.cell(
        row=quality_row,
        column=1,
        value="DATA QUALITY",
    ).font = Font(
        bold=True,
        color=NAVY,
    )

    for row, (name, value) in enumerate(
        cleaning_summary.items(),
        quality_row + 1,
    ):
        summary.cell(
            row=row,
            column=1,
            value=name,
        )
        summary.cell(
            row=row,
            column=2,
            value=value,
        )

    # Top Products
    products["A1"] = "TOP PRODUCTS BY REVENUE"
    products["A1"].font = Font(
        size=16,
        bold=True,
        color=WHITE,
    )
    products["A1"].fill = PatternFill(
        "solid",
        fgColor=NAVY,
    )
    products.merge_cells("A1:D1")

    write_table(
        products,
        report_data["top_products"],
        3,
        "TopProductsTable",
        revenue_threshold,
        color_scale=True,
    )

    for sheet in workbook.worksheets:
        sheet.sheet_view.showGridLines = False
        sheet.freeze_panes = "A4"

        for column in ["A", "B", "C", "D"]:
            sheet.column_dimensions[column].width = 22

    workbook.save(output_file)

    return output_file