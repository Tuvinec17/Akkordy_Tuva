from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

UPLOAD_FOLDER = "static/music"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            lyrics TEXT NOT NULL,
            chords TEXT NOT NULL,
            audio TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()
    return render_template("index.html", songs=songs)

@app.route("/song/<int:song_id>")
def song(song_id):
    conn = get_db_connection()
    song = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
    conn.close()
    if song is None:
        return "Песня не найдена", 404
    return render_template("song.html", song=song)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        lyrics = request.form["lyrics"]
        chords = request.form["chords"]
        audio = None

        if "audio" in request.files:
            file = request.files["audio"]
            if file.filename:
                audio_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(audio_path)
                audio = file.filename

        conn = get_db_connection()
        conn.execute("INSERT INTO songs (title, artist, lyrics, chords, audio) VALUES (?, ?, ?, ?, ?)", 
                     (title, artist, lyrics, chords, audio))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("admin.html")

create_table()

if name == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Берём порт из окружения (Render его подставит)
    app.run(host="0.0.0.0", port=port)  # Открываем доступ извне
