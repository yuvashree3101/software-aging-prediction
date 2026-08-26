import csv
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze


# Project root folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# CSV output location
OUTPUT_FILE = PROJECT_ROOT / "radon_analysis" / "radon_metrics.csv"


# Find all Python files in the project
python_files = []

for file in PROJECT_ROOT.rglob("*.py"):
    if "venv" not in file.parts and "radon_analysis" not in file.parts:
        python_files.append(file)


rows = []

for file_path in python_files:

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        # Cyclomatic Complexity
        complexity_results = cc_visit(code)

        if complexity_results:
            average_complexity = sum(
                item.complexity for item in complexity_results
            ) / len(complexity_results)
        else:
            average_complexity = 0

        # Maintainability Index
        maintainability_index = mi_visit(code, multi=True)

        # Raw metrics
        raw_metrics = analyze(code)

        # Halstead metrics
        halstead = h_visit(code).total

        rows.append([
            str(file_path.relative_to(PROJECT_ROOT)),
            round(average_complexity, 2),
            round(maintainability_index, 2),
            raw_metrics.loc,
            raw_metrics.lloc,
            raw_metrics.sloc,
            raw_metrics.comments,
            raw_metrics.blank,
            round(halstead.volume, 2),
            round(halstead.difficulty, 2),
            round(halstead.effort, 2)
        ])

    except Exception as error:
        print(f"Skipped {file_path}: {error}")


# Write all metrics to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "File",
        "Average_Complexity",
        "Maintainability_Index",
        "LOC",
        "LLOC",
        "SLOC",
        "Comments",
        "Blank_Lines",
        "Halstead_Volume",
        "Halstead_Difficulty",
        "Halstead_Effort"
    ])

    writer.writerows(rows)


print("===================================")
print("Radon analysis completed!")
print(f"Python files analyzed: {len(rows)}")
print(f"CSV created: {OUTPUT_FILE}")
print("===================================")