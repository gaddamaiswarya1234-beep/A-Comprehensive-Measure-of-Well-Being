from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    # Get values from form
    life = float(request.form['life'])
    edu = float(request.form['edu'])
    income = float(request.form['income'])

    # Simple formula (example)
    hdi = (life + edu + income) / 3

    return render_template("index.html", prediction_text=f"HDI Value: {hdi:.2f}")

if __name__ == "__main__":
    app.run()
