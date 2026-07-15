
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    life = float(request.form['life'])
    edu = float(request.form['edu'])
    income = float(request.form['income'])

    hdi = (life + edu + income) / 3

    return render_template("index.html", prediction_text=f"HDI: {hdi:.2f}")

if __name__ == "__main__":
    app.run()
