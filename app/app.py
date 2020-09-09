from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hallopenjos"

@app.route("/about")
def about():
    return "Testing about "
