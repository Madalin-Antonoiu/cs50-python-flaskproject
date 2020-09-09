from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route("/")
def index():
    rnr = random.randint(0, 1)
    return render_template("index.html",  number = rnr)

@app.route("/hello")
def hello():
    text = request.args.get("user_text")
    return render_template("hello.html",  text = text)
