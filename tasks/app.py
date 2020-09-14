from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def tasks():
    return "Tasks"

@app.route("/add")
def add():
    return "Add a new Task"