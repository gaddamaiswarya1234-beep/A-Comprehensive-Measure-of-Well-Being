from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load the trained model and scaler
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Read input values
        health = float(request.form["health"])
        education = float(request.form["education"])
        income = float(request.form["income"])
        environment = float(request.form["environment"])
        safety = float(request.form["safety"])
        social_support = float(request.form["social_support"])

        # Create input array
        features = np.array([[
            health,
            education,
            income,
            environment,
            safety,
            social_support
        ]])

        # Scale the input
        features_scaled = scaler.transform(features)

        # Predict
        prediction = model.predict(features_scaled)

        return render_template(
            "home.html",
            prediction_text=f"Predicted Well-being Score: {prediction[0]:.2f}"
        )

    except Exception as e:
        return render_template(
            "home.html",
            prediction_text=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    app.run(debug=True)