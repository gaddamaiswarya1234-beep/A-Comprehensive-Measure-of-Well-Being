import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Load dataset
data = pd.read_csv(r"..\dataset\Continent_HDI.csv")

# Remove missing values
data = data.dropna()

# Features
X = data[
    [
        "Life_ expectancy",
        "Mean years of schooling",
        "Gross national income (GNI) per capita",
        "Gender Development Index value",
        "Human Development Index (HDI) Female"
    ]
]

# Target
y = data["HDI"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open("HDI.pkl", "wb"))

print("Model trained successfully!")