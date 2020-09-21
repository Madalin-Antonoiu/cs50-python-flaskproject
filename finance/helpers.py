import requests
import os
import urllib.parse
import datetime
import json 

from flask import redirect, render_template, request, session, flash
from functools import wraps
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


def apology(message, category="danger"):
    """Render message as an apology to user."""
    path = request.path
    flash(message, category)
    return render_template(template_name_or_list=path+".html")


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    """Look up quote for symbol."""
    # https://cloud-sse.iexapis.com/stable/stock/TSLA/quote?token={API_KEY} - Works
    # export API_KEY="value"
    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError) as error:
        return (str(error))


# The array must be like aapl,fb,ibm - united with ","
# def multiple_lookup_from_db(username):

#     """Look up quote for multiple symbols from within a database."""
#     # https://sandbox.iexapis.com/stable/stock/market/batch?symbols=aapl,fb,ibm&types=quote&token=Tsk_7c88ae2fc7e24bfdb773cd7a6a518f6e - works
#     # The above is a public API ;)
    
#     try:
#         link = "batch?symbols="
#         symbols = []
#         rows = db.execute("SELECT symbol, shares FROM :username", username=username) #If i query only symbol, they return alphabetically ordered
#         for item in rows:
#             symbols.append(item["symbol"])
#             link = link + item["symbol"].lower() + ","

#         api_key = os.environ.get("API_KEY")
#         response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/market/{link}&types=quote&token={api_key}")
#         response.raise_for_status()

#     except requests.RequestException:
#         return None

#     # # Parse response
#     try:
#         quote = response.json()
#         kkk = []
        
#         for symbol in symbols:
#         # return quote
#             kkk.append(quote[symbol])
#             kkk[symbol]["name"] = quote[symbol]["quote"]["companyName"]
#             kkk[symbol]["price"]= float(quote[symbol]["quote"]["latestPrice"])
#             kkk[symbol]["symbol"] = quote[symbol]["quote"]["symbol"]

#         # json_object = json.dumps(kkk)
#         print(kkk)

#         # return kkk
#             # "name": quote[symbol]["quote"]["companyName"],
#             # "price": float(quote[symbol]["quote"]["latestPrice"]),
#             # "symbol": quote[symbol]["quote"]["symbol"]
#             # json_object
           
        

#     except (KeyError, TypeError, ValueError) as error:
#         return (str(error))



# def usd(value):
#     """Format value as USD."""
#     return f"${value:,.2f}"

