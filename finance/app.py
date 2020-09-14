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
    """Show portfolio of stocks"""
    # return apology("TODO")
    return redirect("/login")

@app.route("/register")
def register():
    return "This is the register page"

@app.route("/login")
def login():
    return render_template("login.html")