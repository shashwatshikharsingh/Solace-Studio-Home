import base64
from flask import Flask, flash, redirect, render_template, request, session,g,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
from helpers import apology, login_required





app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

admin_ids = [1]







def get_db():
    """Open a new database connection if there is none yet for the current application context. Create Tables if they do not exist."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect("users.db")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL)")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT NOT NULL,game_link TEXT NOT NULL,userid INTEGER NOT NULL,is_Verified INTEGER NOT NULL,FOREIGN KEY (userid) REFERENCES users (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS game_images (id INTEGER PRIMARY KEY AUTOINCREMENT,game_id INTEGER NOT NULL,picture TEXT NOT NULL,FOREIGN KEY (game_id) REFERENCES games (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS newsletter (id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL)")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, heading TEXT NOT NULL, subheading TEXT NOT NULL, author TEXT NOT NULL, description TEXT NOT NULL, date TEXT NOT NULL, userid INTEGER NOT NULL, FOREIGN KEY (userid) REFERENCES users (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS event_images (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER NOT NULL, picture TEXT NOT NULL, FOREIGN KEY (event_id) REFERENCES events (id))")
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/",methods=["GET"])
def index():
    """Main Page"""
    return render_template("index.html")

@app.route("/submit",methods=["GET","POST"])
@login_required
def submit():
    """Submit a New Game with Name Descriptions Images in Base64 and Link to the Game"""

    if request.method == "POST":
        
        if not request.form.get("name"):
            return apology("Please Enter a Name")
        if not request.form.get("description"):
            return apology("Please Enter a Description")
        if not request.form.get("game_link"):
            return apology("Please Enter a Game Link")
        if not request.files.getlist("picture"):
            return apology("Please Enter a Picture")
        
        name = request.form.get("name")
        description = request.form.get("description")
        game_link = request.form.get("game_link")
        pictures = request.files.getlist("picture")
        try:
            db = get_db()
            cursor = db.cursor()
        
            cursor.execute("INSERT INTO games (name, description, game_link, userid,is_Verified) VALUES (?, ?, ?, ?,?)", (name, description, game_link, session["user_id"],0))
            game_id = cursor.lastrowid
        
            for picture in pictures:
                picture_string = base64.b64encode(picture.read())
                cursor.execute("INSERT INTO game_images (game_id, picture) VALUES (?, ?)", (game_id, picture_string))
        
            db.commit()
        except Exception as e:
            print(e)
            return apology("Error Submitting Game")
        
        return render_template("submit.html",success=True)
    else:
        return render_template("submit.html")
    
@app.route("/event/<int:id>",methods=["GET"])
def event(id):
    """Event Page for Each Event"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (id,))
        event = cursor.fetchone()
        cursor.execute("SELECT picture FROM event_images WHERE event_id = ?", (id,))
        pictures = cursor.fetchall()
        picture_address = []
        index = 0
        for picture in pictures: 
                image_address = f"./static/temp/events/{event[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
        event_details = {"heading": event[1], "subheading": event[2], "author": event[3], "description": event[4], "date": event[5], "event_images":picture_address}

    except Exception as e:
        print(e)
        return apology("Error Fetching Event")
    return render_template("event.html",event=event_details)


@app.route("/submit_event",methods=["GET","POST"])
@login_required
def submit_event():
    """Submit a New Event with Name Descriptions Images in Base64 and Link to the Event"""
    if session["user_id"] not in admin_ids:
        return apology("You are not authorized to submit events")
    
    if request.method == "POST":
        if not request.form.get("heading"):
            return apology("Please Enter a Heading")
        if not request.form.get("subheading"):
            return apology("Please Enter a Sub Heading")
        if not request.form.get("author"):
            return apology("Please Enter a Author")
        if not request.files.getlist("picture"):
            return apology("Please Enter a Picture")
        if not request.form.get("description"):
            return apology("Please Enter a Description")
        if not request.form.get("date"):
            return apology("Please Enter a Date")
        
        heading = request.form.get("heading")
        subheading = request.form.get("subheading")
        author = request.form.get("author")
        description = request.form.get("description")
        date = request.form.get("date")
        pictures = request.files.getlist("picture")


        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("INSERT INTO events (heading, subheading, author, description, date, userid) VALUES (?, ?, ?, ?, ?, ?)", (heading, subheading, author, description, date, session["user_id"]))
        
            event_id = cursor.lastrowid
        
            for picture in pictures:
                picture_string = base64.b64encode(picture.read())
                cursor.execute("INSERT INTO event_images (event_id, picture) VALUES (?, ?)", (event_id, picture_string))
        
            db.commit()
        except Exception as e:
            print(e)
            return apology("Error Submitting Event")
        
        return render_template("submit_event.html",success=True)
    else:
        return render_template("submit_event.html")




@app.route("/games",methods=["GET"])
def games():
    """Display All Games"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM games WHERE is_Verified = 1")
        games = cursor.fetchall()

        game_details = []

        for game in games:
            cursor.execute("SELECT picture FROM game_images WHERE game_id = ?", (game[0],))
            pictures = cursor.fetchall()
            picture_address = []

            

            if not os.path.exists(f"static/temp/{game[1]}.png"): 
                with open(f"static/temp/{game[1]}.png", "wb") as f:
                    picture_address.append(f"./static/temp/{game[1]}.png")
                    f.write(base64.b64decode(pictures[0][0]))
            else:
                picture_address.append(f"./static/temp/{game[1]}.png")

            game_details.append({"name": game[1], "description": game[2], "game_link": game[3], "pictures": picture_address})
    except Exception as e:
        print(e)
        return apology("Error Fetching Games")
        
    return render_template("games.html",games=game_details)

@app.route("/approve",methods=["GET"])
@login_required
def approve():
    """Approve Games to be Displayed"""
    if session["user_id"] not in admin_ids:
        return apology("You are not authorized to approve games")
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM games WHERE is_Verified = 0")
        games = cursor.fetchall()
        game_details = []

        for game in games:
            cursor.execute("SELECT picture FROM game_images WHERE game_id = ?", (game[0],))
            pictures = cursor.fetchall()
            index = 0
            picture_address = []

            for picture in pictures: 
                image_address = f"./static/temp/admin/{game[1]}-{index}.png"

                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)

                else:
                    picture_address.append(image_address)
                index += 1

            game_details.append({"id":game[0],"name": game[1], "description": game[2], "game_link": game[3], "pictures": picture_address})
    except Exception as e:
        print(e)
        return apology("Error Fetching Games")

    return render_template("approve.html",games=game_details)


@app.route("/accept/<int:id>",methods=["POST"])
@login_required
def accept(id):
    """Accept a Game to be Displayed"""
    if session["user_id"] not in admin_ids:
        return apology("You are not authorized to approve games")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE games SET is_Verified = 1 WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Accepting Game")
    return render_template("approve.html",accept=True)

@app.route("/reject/<int:id>",methods=["POST"])
@login_required
def reject(id):
    """Reject a Game to be Displayed"""
    if session["user_id"] not in admin_ids:
        return apology("You are not authorized to approve games")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Rejecting Game")
    return render_template("approve.html",reject=True)

@app.route("/about",methods=["GET"])
def about():
    """About Page"""
    return render_template("about.html")

@app.route("/subscribe",methods=["POST"])
def subscribe():
    """Subscribe to the Newsletter"""
    email = request.form.get("email")
    if not email:
        return apology("Please Enter an Email")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
        db.commit()
    except Exception as e: 
        print(e)
        return apology("Error Subscribing")
    return render_template("index.html",subscribe=True)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0][0]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Please Enter a Username")
        if not password or not confirmation or password != confirmation:
            return apology("Please correctly write both password fields")

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        duplicate = cursor.fetchone()

        if duplicate:
            return apology("Username already exists")

        passwordHash = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username,hash) VALUES (?, ?)", (username, passwordHash))
        db.commit()

        return redirect("/login")

    else:
        return render_template("register.html")
