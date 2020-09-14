import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import gettempdir

from helpers import *

# configure application
app = Flask(__name__)

# The Model - Connect to database 
db = SQL("sqlite:///finance.db")

# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set.")

@app.route("/")
# @login_required
def index():
    # return apology("TODO")
    """Show portfolio of stocks"""
    return render_template("/index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template( "register.html")
    else:
        username = request.form.get("username")
        if not username:
            return render_template("apology.html", message="You must provide an username.")

        email = request.form.get("email")
        if not email:
            return render_template("apology.html", message="You must provide an email adress.")

        password = request.form.get("password")
        if not password:
            return render_template("apology.html", message="You must provide a password.")

        verify_password = request.form.get("verify_password")
        if not verify_password:
            return render_template( "apology.html", message="You must validate the password.")


        # Only if you write a name and an email ( well, add a letter in each field) you can reach up to here where you write to the DB
        db.execute("INSERT INTO users (email, username, password, verify_password) VALUES (:email, :username, :password, :verify_password);", email=email, username=username, password=password, verify_password=verify_password )
        return redirect("/")

@app.route("/login")
def login():
    rows = db.execute("SELECT * from users;")
    return render_template("login.html", rows=rows)