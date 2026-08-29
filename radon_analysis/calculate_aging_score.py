import pandas as pd

INPUT_FILE = "radon_analysis/aging_dataset.csv"
OUTPUT_FILE = "radon_analysis/aging_dataset_with_score.csv"

print("Calculating software aging score...")

df = pd.read_csv(INPUT_FILE)

# Exclude the initial version because it has no meaningful code metrics
df = df[df["LOC"] > 0].copy()

# Normalize selected aging-related metrics
df["Complexity_Score"] = (
    df["Average_Complexity"] /
    df["Average_Complexity"].max()
)

df["Effort_Score"] = (
    df["Halstead_Effort"] /
    df["Halstead_Effort"].max()
)

df["LOC_Score"] = (
    df["LOC"] /
    df["LOC"].max()
)

# Maintainability decreases as software ages,
# so convert it into an aging score
df["Maintainability_Score"] = (
    1 - df["Maintainability_Index"] /
    df["Maintainability_Index"].max()
)

# Weighted Software Aging Score
df["Aging_Score"] = (
    0.30 * df["Complexity_Score"] +
    0.30 * df["Effort_Score"] +
    0.20 * df["LOC_Score"] +
    0.20 * df["Maintainability_Score"]
)

# Convert score to percentage
df["Aging_Score"] = (df["Aging_Score"] * 100).round(2)

# Assign aging level
def classify_aging(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


df["Aging_Level"] = df["Aging_Score"].apply(classify_aging)

# Save dataset
df.to_csv(OUTPUT_FILE, index=False)

print("========================================")
print("Software aging score calculated!")
print(f"Versions analyzed: {len(df)}")
print(f"CSV created: {OUTPUT_FILE}")
print("========================================")

print("\nAging results:")
print(
    df[
        [
            "Version",
            "LOC",
            "Average_Complexity",
            "Maintainability_Index",
            "Halstead_Effort",
            "Aging_Score",
            "Aging_Level",
        ]
    ].to_string(index=False)
)