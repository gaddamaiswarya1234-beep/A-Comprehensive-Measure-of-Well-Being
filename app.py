from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model
model = pickle.load(open("HDI.pkl", "rb"))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/predict", methods=["POST"])
def predict():
    life = float(request.form["life"])
    school = float(request.form["school"])
    income = float(request.form["income"])
    gender = float(request.form["gender"])
    female = float(request.form["female"])

    features = np.array([[life, school, income, gender, female]])

    prediction = model.predict(features)

    return render_template(
        "home.html",
        prediction_text=f"Predicted HDI: {prediction[0]:.3f}"
    )

if __name__ == "__main__":
    app.run(debug=True)