from flask import Flask

# create app
app = Flask(__name__)

# home route
@app.route('/')
def home():
    return "HDI App Working Successfully ✅"

# extra route (optional test)
@app.route('/predict')
def predict():
    return "Prediction page working 👍"

# for local running
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
