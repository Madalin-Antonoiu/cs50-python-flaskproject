from flask import Flask, render_template
from cs50 import SQL

app = Flask(__name__)
db = SQL("sqlite:///data.db")

@app.route("/")
def index():
    rows = db.execute("SELECT * from registrants;")
    return render_template( "index.html", rows=rows )