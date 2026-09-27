import argparse
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger

from cleaning import load_and_clean_data
from config import load_config
from excel_report import create_excel_report
from reporting import create_report_data, select_reporting_period


PROJECT_ROOT = Path(__file__).resolve().parent


def generate_report():
    """Generate the business report using the configured CSV."""

    config = load_config()

    input_file = PROJECT_ROOT / config["input_file"]

    cleaned_data, cleaning_summary = (
        load_and_clean_data(input_file)
    )

    frequency = config["report"]["frequency"]

    period_data, report_start, report_end = (
        select_reporting_period(
            cleaned_data,
            frequency,
        )
    )

    report_data = create_report_data(period_data)

    output_file = PROJECT_ROOT / config["output_file"]

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

    print(
        f"Report generated: {output_file}"
    )


def run_test_report(scheduler):
    """Run the test report and stop the scheduler."""

    generate_report()
    scheduler.shutdown(wait=False)


def start_scheduler(test_mode=False):
    """Start the automated report scheduler."""

    config = load_config()
    report_config = config["report"]

    scheduler = BlockingScheduler()

    if test_mode:
        test_time = datetime.now() + timedelta(seconds=5)

        scheduler.add_job(
            lambda: run_test_report(scheduler),
            trigger=DateTrigger(run_date=test_time),
        )

        print(
            "Scheduler test started."
        )

        print(
            "Test report will run in approximately 5 seconds."
        )

    else:
        scheduler.add_job(
            generate_report,
            trigger="cron",
            day_of_week=report_config["schedule_day"],
            hour=report_config["schedule_hour"],
            minute=report_config["schedule_minute"],
        )

        print(
            "Scheduler started."
        )

        print(
            f"Report scheduled for "
            f"{report_config['schedule_day']} "
            f"at "
            f"{report_config['schedule_hour']:02d}:"
            f"{report_config['schedule_minute']:02d}."
        )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the automated business report scheduler."
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the scheduled report once after a short delay.",
    )

    args = parser.parse_args()

    start_scheduler(test_mode=args.test)