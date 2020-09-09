from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", name="Madalin")

@app.route("/about")
def about():
    return "Testing about "
