import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

print("======================================")
print("Software Aging Prediction")
print("======================================")

# Load dataset
df = pd.read_csv("radon_analysis/aging_dataset_with_score.csv")

# Remove Version 1 because it is the initial baseline
df = df[df["Version"] > 1]

# Input features
X = df[[
    "LOC",
    "Average_Complexity",
    "Maintainability_Index",
    "Halstead_Effort"
]]

# Target value
y = df["Aging_Score"]

# Create and train model
model = LinearRegression()
model.fit(X, y)

# Predict existing versions
df["Predicted_Aging_Score"] = model.predict(X)

print("\nActual vs Predicted Aging Score:")
print(
    df[
        ["Version", "Aging_Score", "Predicted_Aging_Score"]
    ].to_string(index=False)
)

# Predict next version using latest metrics
latest = df.iloc[-1]

next_version = latest["Version"] + 1

next_data = pd.DataFrame([{
    "LOC": latest["LOC"],
    "Average_Complexity": latest["Average_Complexity"],
    "Maintainability_Index": latest["Maintainability_Index"],
    "Halstead_Effort": latest["Halstead_Effort"]
}])

predicted_score = model.predict(next_data)[0]

print("\n======================================")
print(f"Predicted Aging Score for Version {int(next_version)}: {predicted_score:.2f}")

if predicted_score >= 70:
    level = "High"
elif predicted_score >= 40:
    level = "Medium"
else:
    level = "Low"

print(f"Predicted Aging Level: {level}")
print("======================================")

# Save prediction results
df.to_csv(
    "radon_analysis/aging_predictions.csv",
    index=False
)

print("\nPrediction CSV created:")
print("radon_analysis/aging_predictions.csv")

# Plot actual aging scores
plt.plot(
    df["Version"],
    df["Aging_Score"],
    marker="o",
    label="Actual Aging Score"
)

plt.plot(
    df["Version"],
    df["Predicted_Aging_Score"],
    marker="x",
    label="Predicted Aging Score"
)

plt.xlabel("Software Version")
plt.ylabel("Aging Score")
plt.title("Software Aging Prediction")
plt.legend()
plt.grid(True)

plt.savefig("radon_analysis/aging_prediction_graph.png")

print("Graph created:")
print("radon_analysis/aging_prediction_graph.png")