import csv
import subprocess
from datetime import datetime

from radon.raw import analyze
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit


OUTPUT_FILE = "radon_analysis/aging_dataset.csv"


def run_git(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def get_commits():
    output = run_git([
        "git", "log",
        "--reverse",
        "--format=%H|%ad|%s",
        "--date=short"
    ])

    commits = []

    for line in output.splitlines():
        commit_id, date, message = line.split("|", 2)
        commits.append({
            "commit_id": commit_id,
            "date": date,
            "message": message
        })

    return commits


def get_python_files(commit_id):
    output = run_git([
        "git", "ls-tree",
        "-r",
        "--name-only",
        commit_id
    ])

    return [
        file
        for file in output.splitlines()
        if file.endswith(".py")
    ]


def get_file_content(commit_id, file_path):
    return run_git([
        "git", "show",
        f"{commit_id}:{file_path}"
    ])


def calculate_metrics(source_code):
    raw = analyze(source_code)

    complexity_blocks = cc_visit(source_code)

    if complexity_blocks:
        average_complexity = sum(
            block.complexity for block in complexity_blocks
        ) / len(complexity_blocks)
    else:
        average_complexity = 0

    maintainability = mi_visit(source_code, True)

    halstead = h_visit(source_code).total

    return {
        "LOC": raw.loc,
        "LLOC": raw.lloc,
        "SLOC": raw.sloc,
        "Comments": raw.comments,
        "Blank_Lines": raw.blank,
        "Average_Complexity": round(average_complexity, 2),
        "Maintainability_Index": round(maintainability, 2),
        "Halstead_Volume": round(halstead.volume, 2),
        "Halstead_Difficulty": round(halstead.difficulty, 2),
        "Halstead_Effort": round(halstead.effort, 2)
    }


def get_change_size(commit_id, parent_id=None):
    if parent_id is None:
        return 0, 0

    output = run_git([
        "git", "diff",
        "--numstat",
        parent_id,
        commit_id
    ])

    insertions = 0
    deletions = 0

    for line in output.splitlines():
        parts = line.split("\t")

        if len(parts) >= 2:
            try:
                insertions += int(parts[0])
                deletions += int(parts[1])
            except ValueError:
                pass

    return insertions, deletions


def main():
    print("Building software aging dataset...")
    print("=" * 50)

    commits = get_commits()

    rows = []

    for index, commit in enumerate(commits, start=1):

        commit_id = commit["commit_id"]
        date = commit["date"]
        message = commit["message"]

        print(f"\nAnalyzing commit {index}/{len(commits)}")
        print(f"Commit: {commit_id[:8]}")
        print(f"Message: {message}")

        python_files = get_python_files(commit_id)

        total_metrics = {
            "LOC": 0,
            "LLOC": 0,
            "SLOC": 0,
            "Comments": 0,
            "Blank_Lines": 0,
            "Average_Complexity": 0,
            "Maintainability_Index": 0,
            "Halstead_Volume": 0,
            "Halstead_Difficulty": 0,
            "Halstead_Effort": 0
        }

        complexity_values = []
        mi_values = []

        for file_path in python_files:

            try:
                source_code = get_file_content(
                    commit_id,
                    file_path
                )

                metrics = calculate_metrics(source_code)

                total_metrics["LOC"] += metrics["LOC"]
                total_metrics["LLOC"] += metrics["LLOC"]
                total_metrics["SLOC"] += metrics["SLOC"]
                total_metrics["Comments"] += metrics["Comments"]
                total_metrics["Blank_Lines"] += metrics["Blank_Lines"]
                total_metrics["Halstead_Volume"] += metrics["Halstead_Volume"]
                total_metrics["Halstead_Difficulty"] += metrics["Halstead_Difficulty"]
                total_metrics["Halstead_Effort"] += metrics["Halstead_Effort"]

                complexity_values.append(
                    metrics["Average_Complexity"]
                )

                mi_values.append(
                    metrics["Maintainability_Index"]
                )

            except Exception as error:
                print(f"Skipping {file_path}: {error}")

        if complexity_values:
            total_metrics["Average_Complexity"] = round(
                sum(complexity_values) / len(complexity_values),
                2
            )

        if mi_values:
            total_metrics["Maintainability_Index"] = round(
                sum(mi_values) / len(mi_values),
                2
            )

        parent_id = (
            commits[index - 2]["commit_id"]
            if index > 1
            else None
        )

        insertions, deletions = get_change_size(
            commit_id,
            parent_id
        )

        row = {
            "Version": index,
            "Commit_ID": commit_id[:8],
            "Date": date,
            "Commit_Message": message,
            "Python_Files": len(python_files),
            "LOC": total_metrics["LOC"],
            "LLOC": total_metrics["LLOC"],
            "SLOC": total_metrics["SLOC"],
            "Comments": total_metrics["Comments"],
            "Blank_Lines": total_metrics["Blank_Lines"],
            "Average_Complexity": total_metrics["Average_Complexity"],
            "Maintainability_Index": total_metrics["Maintainability_Index"],
            "Halstead_Volume": round(total_metrics["Halstead_Volume"], 2),
            "Halstead_Difficulty": round(total_metrics["Halstead_Difficulty"], 2),
            "Halstead_Effort": round(total_metrics["Halstead_Effort"], 2),
            "Insertions": insertions,
            "Deletions": deletions
        }

        rows.append(row)

    fieldnames = list(rows[0].keys())

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 50)
    print("Software aging dataset created successfully!")
    print(f"Versions analyzed: {len(rows)}")
    print(f"CSV created: {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()