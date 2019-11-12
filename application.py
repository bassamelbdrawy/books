import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for,Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, allowed_file
import csv
import pymysql
import requests
pymysql.install_as_MySQLdb()

UPLOAD_FOLDER = './storage/'
# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True
#set folder path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use mysql database
db = SQL('mysql://root:01017876733@localhost/book')

@app.route("/")
@login_required
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", message = "missing username")
        elif not request.form.get("password"):
            return render_template("apology.html", message = "missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", message = "passwords doesnt match")
        else:
            rows = db.execute("INSERT INTO users (username,password) VALUES (:userName, :password)",
                              userName=request.form.get("username"), password=generate_password_hash(request.form.get("password")))
            session['user_id'] = rows
            if not rows:
                return render_template("apology.html", message = "username is not available")
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message = "missing username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message = "missing password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("apology.html", message = "invalid username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":

        rows = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author"
         , isbn = '%' + request.form.get("search") + '%', title = '%' + request.form.get("search") + '%', author = '%' + request.form.get("search") + '%'  )
        if len(rows):
            return render_template("search.html", rows = rows)
        else:
            return render_template("apology.html" , message = "NO RESULT")
    return redirect("/")


@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method == "GET":
        rows = db.execute("SELECT * FROM books WHERE isbn = :isbn" , isbn = isbn)
        data = db.execute("SELECT * FROM reviews WHERE bookisbn = :isbn", isbn = isbn)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vcWcLCQCzwOv3tNTfBHFg", "isbns": isbn })
        ress = res.json()
        return render_template("book.html", rows=rows , data = data , ress = ress)
    if request.method == "POST":
        comments = db.execute("SELECT * FROM reviews WHERE bookisbn = :isbn" , isbn = isbn)
        if len(comments):
            for comment in comments:
                if comment["userid"] == session["user_id"]:
                    flash("you had rate this book before")
                    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn" , isbn = isbn)
                    data = db.execute("SELECT * FROM reviews WHERE bookisbn = :isbn", isbn = isbn)
                    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vcWcLCQCzwOv3tNTfBHFg", "isbns": isbn })
                    ress = res.json()
                    return render_template("book.html", rows=rows , data = data , ress = ress)
                    return render_template("book.html" ,rows=rows , data = data)
        rows = db.execute("INSERT INTO reviews (review,rate,bookisbn,userid) VALUES (:review,:rate,:bookisbn,:userid)",
        review = request.form.get("review") , rate = request.form.get("rate") , bookisbn = isbn , userid = session["user_id"])
        rows = db.execute("SELECT * FROM books WHERE isbn = :isbn" , isbn = isbn)
        data = db.execute("SELECT * FROM reviews WHERE bookisbn = :isbn", isbn = isbn)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vcWcLCQCzwOv3tNTfBHFg", "isbns": isbn })
        ress = res.json()
        return render_template("book.html", rows=rows , data = data , ress = ress)

@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api(isbn):
    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn" , isbn = isbn)
    data = db.execute("SELECT * FROM reviews WHERE bookisbn = :isbn", isbn = isbn)
    return jsonify(rows,data)

@app.route("/logout")
def logout(): 
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




