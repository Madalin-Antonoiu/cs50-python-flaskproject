import os
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, request, g
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology, lookup

# Configure application
app = Flask(__name__)

# .env setup for the API
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# The Model - Connect to database 
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")#✔️
@login_required
def index():
    # SELECT currency would be better
    """Show portfolio of stocks"""
    final_quotes = []

    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
    currency = rows[0]["currency"]
    
    user_table = db.execute("SELECT symbol, shares, company FROM :username", username=session["username"]) #If i query only symbol, they return alphabetically ordered
    
    for row in user_table:
      quote = lookup(row["symbol"]) # do these in deffered JavaScript ajax, like this it takes too long (2-3 sec) and for no good reason!
      
      # + Add shares
      quote["shares"] = row["shares"]
      quote["total"] = round(quote["shares"] * quote["price"],2)
      final_quotes.append(quote)

    # json_object = multiple_lookup_from_db(session["username"])

    return render_template("/index.html", currency=currency, final_quotes=final_quotes)

@app.route("/register", methods=["GET", "POST"])#✔️
def register():
    if request.method == 'POST':
        """Register user"""
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        status = True
        
        # check username
        if not request.form.get('username'):
            status = False
            return apology("You must provide an username")

        # check password
        if not request.form.get('password'):
            status = False
            return apology("You must provide a password")

        # check password confirmation
        if not request.form.get('password') == request.form.get('confirm_password'):
            status = False
            return apology("Password confirmation not match")

        # check unique username
        exists_username= db.execute("SELECT username FROM users where username = :username", username = username)
        if exists_username:
            status = False
            return apology("Username already taken")

        # If the program didn't get into any of the above for the status to get false, it means we' re all good
        if status:
            # register
            register = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = username, hash = password)

            # Remember which user has logged in
            session["user_id"] = register
            session["username"] = username

            CREATE_USER_TABLE = db.execute("""CREATE TABLE :user (
                                                symbol  STRING UNIQUE PRIMARY KEY,
                                                company STRING (1000) ,
                                                shares  INTEGER)""", user=username)

            flash("You are now registered.", "success")
            # Redirect user to home page
            return render_template("index.html", code=True)

        # return render_template('register.html', status = status, text = text)
    else:
        return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])#✔️
def login():
    """Log user in"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        rows = db.execute("SELECT * from users;") # Troubleshooting registered users, can be removed

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You must provide an username") #rows can be removed from apology

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("You must provide a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
      
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password")
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        
        flash('Successfully logged in.', "success")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        if "user_id" in session:
            flash('Already logged in, redirected to home page.', "success")
            return redirect("/")

        return render_template("login.html")

@app.route("/logout")#✔️
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("Successfully logged out.", "success")
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])#✔️
@login_required
def quote():
    """Lookup for symbol"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide a symbol e.g TSLA") 
        
        symbol = request.form.get('symbol')
        quote = lookup(symbol)

        if not quote:
            return apology("Symbol not found.")

        return render_template('quote.html', quote = quote)

        # return apology("Work in Progress" , 201, "quote.html") 
    else:
        # """Get stock quote."""
        return render_template("quote.html")
        
@app.route("/buy", methods=["GET", "POST"])#✔️
@login_required
def buy():
    if request.method == "POST":

        # Get the time of the request in dt_string
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        symbol = request.form.get('symbol')
        
        if not request.form.get("symbol"):
            return apology("Must must type in a symbol, e.g TSLA") 
        
        # Make sure it is integer, and always positive (abs)
        # I also forbid negative value in front end
        # If by any means it gets negative, it does the reverse ( SELL!)
        shares = abs(int(request.form.get('shares'))) 

        if not request.form.get("shares"):
            return apology("You must type in how many shares you want to purchase.") 
        
        quote = lookup(symbol)

        if not quote:
            return apology("Symbol not valid.")
        
        # check if enough cash left
        #create history entry and remove cash

        # Get the active currency
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        session["currency"] = rows[0]["currency"]

        # if positive
        if session["currency"] > 0:
            #move on, cut the price from it
            # calculate the price of what you want to buy, see if it`s lower than your session currency
            session["purchase_total"] =  round(quote["price"] * shares, 2)

            # if active currency is bigger than purchase_total

            if session["currency"] > session["purchase_total"]:

                #update the users table and insert the symbol and shares

                # SELECT symbol row from table
                rows = db.execute("SELECT * FROM :table WHERE symbol = :symbol ", table=session["username"], symbol=symbol)

                # if found same symbol in retrieved data from user's table, update shares count
                if rows:

                    # I moved it here because i dont want to take money away if an error happen with the shares
                    # calculate remaining currency and update  currency in db 
   
                    session["updated_currency"] = round(session["currency"] - session["purchase_total"], 2)
                    UPDATE_CURRENCY = db.execute("UPDATE users SET currency = :updated_currency WHERE id = :id", updated_currency=session["updated_currency"], id=session["user_id"])

                    count = rows[0]["shares"] + shares
                    #update shares
                    UPDATE_SHARES = db.execute("UPDATE :user_table SET shares = :count WHERE symbol = :symbol", user_table=session["username"], count=count, symbol=symbol)

                    # And write to history too!
                    UPDATE_HISTORY = db.execute("""
                                        INSERT INTO history (id, username, symbol, company, shares, price, currency_before, currency_after, transacted) 
                                        VALUES(:id, :username, :symbol, :company, :shares, :price, :currency_before, :currency_after, :transacted)
                                        """, 
                                        id =session["user_id"], 
                                        username=session["username"], 
                                        symbol=symbol, company=quote["name"], 
                                        shares=shares, 
                                        price=session["purchase_total"], 
                                        currency_before=session["currency"], 
                                        currency_after=session["updated_currency"], 
                                        transacted=dt_string)

                    # Congratulate message and redirect to index
                    flash("Successfully purchased" + " " + str(shares) + "x" + " " + quote["symbol"] + " at" + " $" + str(quote["price"]) + " each" , "success"  )
                    return redirect('/')
                else:
                    # I moved it here because i dont want to take money away if an error happen with the shares
                    # calculate remaining currency and update  currency in db 
                    session["updated_currency"] = round(session["currency"] - session["purchase_total"], 2)
                    UPDATE_CURRENCY = db.execute("UPDATE users SET currency = :updated_currency WHERE id = :id", updated_currency=session["updated_currency"], id=session["user_id"])


                    #update shares, insert shares
                    UPDATE_SHARES = db.execute("""
                                    INSERT INTO :user_table (symbol, company, shares)
                                    VALUES (:symbol, :company, :shares)
                                    """, user_table=session["username"], symbol=symbol, company=quote["name"], shares=shares)

                                            # And write to history too!
                    UPDATE_HISTORY = db.execute("""
                                        INSERT INTO history (id, username, symbol, company, shares, price, currency_before, currency_after, transacted) 
                                        VALUES(:id, :username, :symbol, :company, :shares, :price, :currency_before, :currency_after, :transacted)
                                        """, 
                                        id =session["user_id"], 
                                        username=session["username"], 
                                        symbol=symbol, company=quote["name"], 
                                        shares=shares, 
                                        price=session["purchase_total"], 
                                        currency_before=session["currency"], 
                                        currency_after=session["updated_currency"], 
                                        transacted=dt_string)

                    # Congratulate message and redirect to index
                    flash("Successfully purchased" + " " + str(shares) + "x" + " " + quote["symbol"] + " at" + " $" + str(quote["price"]) + " each ", "success"  )
                    return redirect('/')
            else:
                return apology("Insufficient funds")
            
        else:
            return apology("Your balance is negative")
        




        # return apology("Work in Progress" , 201, "quote.html") 
    else:
        # """Get stock quote."""
        return render_template("/buy.html")

@app.route("/sell", methods=["GET", "POST"])#✔️
@login_required
def sell():
    if request.method == "POST":

        # Get the time of the request in dt_string
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        symbol = request.form.get('symbol')
        
        if not request.form.get("symbol"):
            return apology("You must type a symbol, e.g TSLA") 
        
        # If by any means it gets negative, it does the reverse ( SELL!)
        shares = abs(int(request.form.get('shares'))) 

        if not request.form.get("shares"):
            return apology("You must type a share count") 
        
        # Get the active symbols and shares max
        rows = db.execute("SELECT * FROM :user_table", user_table=session["username"])

        for row in rows:
            # If we find the selected symbol in the database ( this is 2nd check, i already get these in GET)
            if symbol == row["symbol"]:
                # We are in the correct symbol row, so by calling row["shares"] we get that row's share count :)
                if shares <= row["shares"]:
                    # SELL THEM

                    # 1. Get its most current price
                    quote = lookup(row["symbol"])

                    if not quote:
                        return apology("Invalid symbol")
                    
                    #2. Substract the shares from total
                    remaining_shares = row["shares"] - shares

                    # Toget rid of TSLA: 0 displays, i need to remove row from table when shares = row[shares]
                    if shares == row["shares"]:
                        UPDATE_SHARES = db.execute("DELETE FROM :user_table WHERE symbol = :symbol", user_table=session["username"], symbol=symbol)
                        
                    UPDATE_SHARES = db.execute("UPDATE :user_table SET shares = :count WHERE symbol = :symbol", user_table=session["username"], count=remaining_shares, symbol=symbol)

                    #3. Add the money to the balance ( Calculate total sale, then add it to currency)
                    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
                    currency_before = rows[0]["currency"]
                    sale = round(shares * quote["price"], 2)
                    total_currency = round(rows[0]["currency"] + sale, 2)
                    UPDATE_CURRENCY = db.execute("UPDATE users SET currency = :total_currency WHERE id = :id", total_currency=total_currency, id=session["user_id"])

                    #4. Add history record
                    UPDATE_HISTORY = db.execute("""
                                    INSERT INTO history (id, username, symbol, company, shares, price, currency_before, currency_after, transacted) 
                                    VALUES(:id, :username, :symbol, :company, :shares, :price, :currency_before, :currency_after, :transacted)
                                    """, 
                                    id =session["user_id"], 
                                    username=session["username"], 
                                    symbol=symbol, 
                                    company=quote["name"], 
                                    shares=-shares, 
                                    price=sale, 
                                    currency_before=currency_before, 
                                    currency_after=total_currency, 
                                    transacted=dt_string)

                    #Congratulate and redirect
                    flash("You have sold " + str(shares) + " x " + symbol + " for " + " " + "$" +str(sale), "success")
                    return redirect("/")
                else:
                    return apology("You do not own that many shares to sell.")

    else:
        """Get available symbols to pick from and their max share count currently owned from the user database"""
        user_table = db.execute("SELECT symbol, shares FROM :username", username=session["username"]) #If i query only symbol, they return alphabetically ordered
        return render_template("/sell.html", data=user_table)

@app.route("/history")#✔️
@login_required
def history():
    rows = db.execute("SELECT * FROM history WHERE id = :id", id=session["user_id"])
    return render_template("/history.html", rows=rows)
