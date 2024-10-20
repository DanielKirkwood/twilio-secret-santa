import csv
import json


def export_report_to_csv(report: list[str], file_name: str):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in report:
            writer.writerow([line])
    print(f"Report saved to {file_name}")


def export_report_to_json(report: list[str], file_name: str):
    with open(file_name, 'w') as jsonfile:
        json.dump(report, jsonfile, indent=4)
    print(f"Report saved to {file_name}")
