import base64
from flask import Flask, flash, redirect, render_template, request, session,g,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
from helpers import apology, login_required
import csv
from datetime import datetime




app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



def get_db():
    """Open a new database connection if there is none yet for the current application context. Create Tables if they do not exist."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect("users.db")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL,email TEXT NOT NULL, is_admin INTEGER NOT NULL)")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT NOT NULL,game_link TEXT NOT NULL,userid INTEGER NOT NULL,is_Verified INTEGER NOT NULL,FOREIGN KEY (userid) REFERENCES users (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS game_images (id INTEGER PRIMARY KEY AUTOINCREMENT,game_id INTEGER NOT NULL,picture TEXT NOT NULL,FOREIGN KEY (game_id) REFERENCES games (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS newsletter (id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL)")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, heading TEXT NOT NULL, subheading TEXT NOT NULL, author TEXT NOT NULL, description TEXT NOT NULL, date TEXT NOT NULL, userid INTEGER NOT NULL, FOREIGN KEY (userid) REFERENCES users (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS event_images (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER NOT NULL, picture TEXT NOT NULL, FOREIGN KEY (event_id) REFERENCES events (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS core (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, team TEXT NOT NULL, core_name TEXT NOT NULL, linkedin TEXT NOT NULL, instagram TEXT NOT NULL, role TEXT NOT NULL)")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS core_images (id INTEGER PRIMARY KEY AUTOINCREMENT, core_id INTEGER NOT NULL, picture TEXT NOT NULL, FOREIGN KEY (core_id) REFERENCES core (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS blogs (id INTEGER PRIMARY KEY AUTOINCREMENT, heading TEXT NOT NULL, subheading TEXT NOT NULL, author TEXT NOT NULL, description TEXT NOT NULL, date TEXT NOT NULL, userid INTEGER NOT NULL, FOREIGN KEY (userid) REFERENCES users (id))")
        g.sqlite_db.execute("CREATE TABLE IF NOT EXISTS blog_images (id INTEGER PRIMARY KEY AUTOINCREMENT, blog_id INTEGER NOT NULL, picture TEXT NOT NULL, FOREIGN KEY (blog_id) REFERENCES blogs (id))")
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def make_temp_dir():
    """Make a temp directory to store images"""
    if not os.path.exists("static/temp"):
        os.makedirs("static/temp")
    if not os.path.exists("static/temp/admin"):
        os.makedirs("static/temp/admin")
    if not os.path.exists("static/temp/core"):
        os.makedirs("static/temp/core")
    if not os.path.exists("static/temp/events"):
        os.makedirs("static/temp/events")
    if not os.path.exists("static/temp/newsletter"):
        os.makedirs("static/temp/newsletter")
    if not os.path.exists("static/temp/blogs"):
        os.makedirs("static/temp/blogs")

make_temp_dir()


@app.route("/",methods=["GET"])
def index():
    """Main Page"""
    return render_template("index.html",current_date=datetime.now().strftime("%Y-%m-%d"))

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
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    
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
    
@app.route("/core",methods=["GET","POST"])
@login_required
def core():
    """Add Core Members"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    if request.method == "POST":
        name = request.form.get("name")
        team = request.form.get("team")
        core_name = request.form.get("core_name")
        linkedin = request.form.get("linkedin")
        instagram = request.form.get("instagram")
        pictures = request.files.getlist("picture")
        role = request.form.get("role") 

        if not name:
            return apology("Please Enter a Name")
        if not team:
            return apology("Please Enter a Team")
        if not core_name and (core_name != "Junior Core" or core_name != "Senior Core"):
            return apology("Please Enter Corrent Core Name. Junior Core / Senior Core")
        if role and core_name == "Junior Core":
            return apology("Junior Core Members cannot have a role")
        if not role and core_name == "Junior Core":
            role = "Core Member"
        if not linkedin:
            return apology("Please Enter a LinkedIn URL")
        if not instagram:
            return apology("Please Enter an Instagram URL")
        if not request.files.getlist("picture"):
            return apology("Please Enter a Headshot")
        
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("INSERT INTO core (name, team, core_name, linkedin, instagram, role) VALUES (?, ?, ?, ?, ?, ?)", (name, team, core_name, linkedin, instagram, role))

            core_id = cursor.lastrowid
        
            for picture in pictures:
                picture_string = base64.b64encode(picture.read())
                cursor.execute("INSERT INTO core_images (core_id, picture) VALUES (?, ?)", (core_id, picture_string))
            db.commit()
        except Exception as e:
            print(e)
            return apology("Error Submitting Core Member")
        
        return render_template("core.html",success=True)
    else:
        return render_template("core.html")
    
@app.route("/manage_core",methods=["GET"])
@login_required
def manage_core():
    """Manage Core Members"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM core")
        core = cursor.fetchall()
        core_details = []
        for member in core:
            cursor.execute("SELECT picture FROM core_images WHERE core_id = ?", (member[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            for picture in pictures: 
                image_address = f"./static/temp/core/{member[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
            core_details.append({"id":member[0],"name": member[1], "team": member[2], "core_name": member[3], "linkedin": member[4], "instagram": member[5], "pictures":picture_address,"role":member[6]})
    except Exception as e:
        print(e)
        return apology("Error Fetching Core Members")
    return render_template("manage_core.html",core=core_details)

@app.route("/remove_core_member/<int:id>",methods=["POST"])
@login_required
def remove_core_member(id):
    """Remove a Core Member"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM core WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Removing Core Member")
    return render_template("manage_core.html",core_deleted=True)
    

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

@app.route("/manage_users",methods=["GET","POST"])
@login_required
def manage_users():
    """Manage Users"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin and session["user_id"] != 1:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        users_details = []
        for user in users:
            cursor.execute("SELECT * FROM games WHERE userid = ?", (user[0],))
            games = cursor.fetchall()
            games = [game[1] for game in games]
            cursor.execute("SELECT * FROM events WHERE userid = ?", (user[0],))
            events = cursor.fetchall()
            events = [event[1] for event in events]
            users_details.append({"id":user[0],"username": user[1], "email": user[3], "is_admin": user[4], "games": games, "events": events})
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    return render_template("manage_users.html",users=users_details)

@app.route("/make_admin/<int:id>",methods=["POST"])
@login_required
def make_admin(id):
    """Make a User Admin"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin and session["user_id"] != 1:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Making User Admin")
    return render_template("manage_users.html",make_admin=True)

@app.route("/remove_admin/<int:id>",methods=["POST"])
@login_required
def remove_admin(id):
    """Remove a User Admin"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET is_admin = 0 WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Removing User Admin")
    return render_template("manage_users.html",remove_admin=True)

@app.route("/approve",methods=["GET"])
@login_required
def approve():
    """Approve Games to be Displayed"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Games")
    except Exception as e:
        print(e)  
        return apology("Error Fetching Users")
    
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
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
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
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage users")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
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
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM core")
        core = cursor.fetchall()
        core_details = []
        if len(core) == 0:
            return render_template("about.html")
        for member in core:
            cursor.execute("SELECT picture FROM core_images WHERE core_id = ?", (member[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            for picture in pictures: 
                image_address = f"./static/temp/core/{member[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
            core_details.append({"name": member[1], "team": member[2], "core_name": member[3], "linkedin": member[4], "instagram": member[5], "pictures":picture_address, "role":member[6]})
    except Exception as e:
        print(e)
        return apology("Error Fetching Core Members")
    
    return render_template("about.html",core=core_details)

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


@app.route("/events",methods=["GET"])
def events():
    """Display All Events"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        event_details = []
        for event in events:
            cursor.execute("SELECT picture FROM event_images WHERE event_id = ?", (event[0],))
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
            event_details.append({"id":event[0],"heading": event[1], "subheading": event[2], "author": event[3], "description": event[4], "date": event[5], "event_images":picture_address})
    except Exception as e:
        print(e)
        return apology("Error Fetching Events")
    return render_template("events.html",events=event_details)

@app.route("/manage_events",methods=["GET"])
@login_required
def manage_events():
    """Manage Events"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Events")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        event_details = []
        
        for event in events:
            cursor.execute("SELECT picture FROM event_images WHERE event_id = ?", (event[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            event_creator_email = cursor.execute("SELECT email FROM users WHERE id = ?", (event[6],)).fetchone()[0]
            for picture in pictures: 
                image_address = f"./static/temp/events/{event[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
            event_details.append({"id":event[0],"heading": event[1], "subheading": event[2], "author": event[3], "description": event[4], "date": event[5], "event_images":picture_address, "user_name":event_creator_email})
    except Exception as e:
        print(e)
        return apology("Error Fetching Events")
    return render_template("manage_events.html",events=event_details)

@app.route("/delete_event/<int:id>",methods=["POST"])
@login_required
def delete_event(id):
    """Delete an Event"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Events")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Deleting Event")
    return render_template("manage_events.html",event_deleted=True)


@app.route("/manage_newsletter",methods=["GET"])
@login_required
def manage_newsletter():
    """Manage Newsletter"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Newsletter")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM newsletter")
        emails = cursor.fetchall()
        email_details = []
        for email in emails:
            email_details.append({"id":email[0],"email": email[1]})
    except Exception as e:
        print(e)
        return apology("Error Fetching Emails")
    return render_template("manage_newsletter.html",newsletter=email_details)

@app.route("/export_newsletter",methods=["POST"])
@login_required
def export_newsletter():
    """Export Newsletter"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Newsletter")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM newsletter")
        emails = cursor.fetchall()
        csv_path = f"./static/temp/newsletter/emails.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'email'])
            for email in emails:
                writer.writerow([email[0], email[1]])
    except Exception as e:
        print(e)
        return apology("Error Exporting Emails")
    return render_template("manage_newsletter.html",newsletter_exported=True, csv_path=csv_path)


@app.route("/manage_games",methods=["GET"])
@login_required
def manage_games():
    """Manage Games"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Games")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM games")
        games = cursor.fetchall()
        game_details = []
        for game in games:
            cursor.execute("SELECT picture FROM game_images WHERE game_id = ?", (game[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            for picture in pictures: 
                image_address = f"./static/temp/{game[1]}-{index}.png"
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
    return render_template("manage_games.html",games=game_details)

@app.route("/delete_game/<int:id>",methods=["POST"])
@login_required
def delete_game(id):
    """Delete a Game"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Games")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Deleting Game")
    return render_template("manage_games.html",game_deleted=True)


@app.route("/submit_blog",methods=["GET","POST"])
@login_required
def submit_blog():
    """Submit a New Blog"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Blogs")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
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

            cursor.execute("INSERT INTO blogs (heading, subheading, author, description, date, userid) VALUES (?, ?, ?, ?, ?, ?)", (heading, subheading, author, description, date, session["user_id"]))
        
            blog_id = cursor.lastrowid
        
            for picture in pictures:
                picture_string = base64.b64encode(picture.read())
                cursor.execute("INSERT INTO blog_images (blog_id, picture) VALUES (?, ?)", (blog_id, picture_string))
        
            db.commit()
        except Exception as e:
            print(e)
            return apology("Error Submitting Blog")
        
        return render_template("submit_blog.html",success=True)
    else:
        return render_template("submit_blog.html")
    
@app.route("/manage_blogs",methods=["GET"])
@login_required
def manage_blogs():
    """Manage Blogs"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Blogs")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blogs")
        blogs = cursor.fetchall()
        blog_details = []
        for blog in blogs:
            cursor.execute("SELECT picture FROM blog_images WHERE blog_id = ?", (blog[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            blog_creator_email = cursor.execute("SELECT email FROM users WHERE id = ?", (blog[6],)).fetchone()[0]
            for picture in pictures: 
                image_address = f"./static/temp/blogs/{blog[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
            blog_details.append({"id":blog[0],"heading": blog[1], "subheading": blog[2], "author": blog[3], "description": blog[4], "date": blog[5], "blog_images":picture_address, "user_name":blog_creator_email})
    except Exception as e:
        print(e)
        return apology("Error Fetching Blogs")
    return render_template("manage_blogs.html",blogs=blog_details)

@app.route("/delete_blog/<int:id>",methods=["POST"])
@login_required
def delete_blog(id):
    """Delete a Blog"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],))
        is_admin = cursor.fetchone()[0]
        if not is_admin:
            return apology("You are not authorized to manage Blogs")
    except Exception as e:
        print(e)
        return apology("Error Fetching Users")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM blogs WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        print(e)
        return apology("Error Deleting Blog")
    return render_template("manage_blogs.html",blog_deleted=True)

@app.route("/blog/<int:id>",methods=["GET"])
def blog(id):
    """Blog Page for Each Blog"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blogs WHERE id = ?", (id,))
        blog = cursor.fetchone()
        cursor.execute("SELECT picture FROM blog_images WHERE blog_id = ?", (id,))
        pictures = cursor.fetchall()
        picture_address = []
        index = 0
        for picture in pictures: 
                image_address = f"./static/temp/blogs/{blog[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
        blog_details = {"heading": blog[1], "subheading": blog[2], "author": blog[3], "description": blog[4], "date": blog[5], "blog_images":picture_address}

    except Exception as e:
        print(e)
        return apology("Error Fetching Blog")
    return render_template("blog.html",blog=blog_details)

@app.route("/blogs",methods=["GET"])
def blogs():
    """Display All Blogs"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blogs")
        blogs = cursor.fetchall()
        blog_details = []
        for blog in blogs:
            cursor.execute("SELECT picture FROM blog_images WHERE blog_id = ?", (blog[0],))
            pictures = cursor.fetchall()
            picture_address = []
            index = 0
            for picture in pictures: 
                image_address = f"./static/temp/blogs/{blog[1]}-{index}.png"
                if not os.path.exists(image_address): 
                    with open(image_address, "wb") as f:
                        f.write(base64.b64decode(picture[0]))
                    picture_address.append(image_address)
                else:
                    picture_address.append(image_address)
                index += 1
            blog_details.append({"id": blog[0], "heading": blog[1], "subheading": blog[2], "author": blog[3], "description": blog[4], "date": blog[5], "blog_images":picture_address})
    except Exception as e:
        print(e)
        return apology("Error Fetching Blogs")
    return render_template("blogs.html",blogs=blog_details)


@app.route("/navigation",methods=["GET"])
def navigation():
    """Navigation Page"""
    return render_template("navigation.html")


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
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        

        if not username:
            return apology("Please Enter a Username")
        if not password or not confirmation or password != confirmation:
            return apology("Please correctly write both password fields")
        if not email:
            return apology("Please Enter an Email")

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        duplicate = cursor.fetchone()

        if duplicate:
            return apology("Username already exists")

        passwordHash = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username,hash,email,is_admin) VALUES (?, ?,?,?)", (username, passwordHash,email,0))
        db.commit()

        return redirect("/login")

    else:
        return render_template("register.html")
