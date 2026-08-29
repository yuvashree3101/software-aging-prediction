import subprocess
import csv
import os

OUTPUT_FILE = "radon_analysis/evolution_metrics.csv"

print("Collecting Git evolutionary metrics...")

# Get Git commit history
result = subprocess.run(
    ["git", "log", "--pretty=format:%H|%ad|%s", "--date=short"],
    capture_output=True,
    text=True
)

commits = result.stdout.strip().split("\n")

rows = []

for commit in commits:
    if not commit:
        continue

    parts = commit.split("|", 2)

    commit_hash = parts[0]
    commit_date = parts[1]
    commit_message = parts[2]

    # Get changes introduced by this commit
    diff_result = subprocess.run(
        ["git", "show", "--stat", "--oneline", commit_hash],
        capture_output=True,
        text=True
    )

    diff_text = diff_result.stdout

    rows.append([
        commit_hash[:8],
        commit_date,
        commit_message,
        diff_text
    ])

# Create CSV file
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Commit_ID",
        "Date",
        "Commit_Message",
        "Change_Summary"
    ])

    writer.writerows(rows)

print("======================================")
print("Git evolutionary metrics collected!")
print(f"Commits analyzed: {len(rows)}")
print(f"CSV created: {OUTPUT_FILE}")
print("======================================")