import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import *

# configure application
app = Flask(__name__)

# The Model - Connect to database 
db = SQL("sqlite:///finance.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set.")

@app.route("/")
@login_required
def index():
    # return apology("TODO", 202)
    """Show portfolio of stocks"""
    return render_template("/index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        """Register user"""
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        status = True
        
        # check username
        if not request.form.get('username'):
            status = False
            return apology("You must provide an username", 403, "register.html")

        # check password
        if not request.form.get('password'):
            status = False
            return apology("You must provide a password", 403, "register.html")

        # check password confirmation
        if not request.form.get('password') == request.form.get('confirm_password'):
            status = False
            return apology("Password confirmation not match", 403, "register.html")

        # check unique username
        exists_username= db.execute("SELECT username FROM users where username = :username", username = username)
        if exists_username:
            status = False
            return apology("Username already taken by another user")

        # If the program didn't get into any of the above for the status to get false, it means we' re all good
        if status:
            # register
            register = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = username, hash = password)

            # Remember which user has logged in
            session["user_id"] = register

            # Redirect user to home page
            return redirect("/")

        # return render_template('register.html', status = status, text = text)
    else:
        return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        rows = db.execute("SELECT * from users;") # Troubleshooting registered users, can be removed

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username" , 403, "login.html") #rows can be removed from apology

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password",  403, "login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403, "login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        rows = db.execute("SELECT * from users;")
        return render_template("login.html", rows=rows)