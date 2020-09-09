from flask import Flask, render_template
import random

app = Flask(__name__)

@app.route("/")
def index():
    onetoten = random.randint(0, 10)
    rnr = random.randint(0, 1)
    return render_template("index.html", name="Madalin", number = rnr, onetoten=onetoten)

@app.route("/about")
def about():
    return "Testing about "
