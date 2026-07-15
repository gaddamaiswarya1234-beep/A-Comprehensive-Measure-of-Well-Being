import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import pickle

# Load dataset
data = pd.read_csv("wellbeing_scores.csv")

# Select features (X) and target (y)
# Adjust column names if needed
X = data[["Continent", "GDP per capita", "Life Expectancy", "Education Index"]]
y = data["HDI"]

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scaling
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create model
model = LinearRegression()

# Train model
model.fit(X_train_scaled, y_train)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

# Save scaler
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("✅ Model and scaler saved successfully!")