import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.utils import secure_filename
import csv
import pymysql
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
def getbooks():
    file = open("books.csv", "r")
    reader = csv.reader(file)
    for row in reader:
        data = db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)", 
        isbn = row[0], title = row[1], author = row[2], year = row[3])
    return True
    