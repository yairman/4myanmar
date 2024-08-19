from cs50 import SQL
from flask import Flask, request, redirect, render_template, flash, session, jsonify
from flask_session import Session
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# I could create the db file using schema.sql file but I'll save it for later.
db = SQL("sqlite:///4myanmar.db")

upload_folder = "static/media"
app.config['UPLOAD_FOLDER'] = upload_folder

# In this case, a dictionary may be less secure but it's easier to manage.
# Add any category that you like.
BOARDS = {
    "General Discussion": "general",
    "Technology": "tech",
    "Gaming": "gaming",
    "Anime & Manga": "anime",
    "Movies": "movies",
    "Music": "music",
    "Books & Literature": "books",
    "Art & Design": "art",
    "Sports": "sports",
    "Science": "science",
    "coding": "coding",
    "Food & Cooking": "food",
    "Fitness & Health": "fitness",
    "Fashion & Beauty": "fashion",
    "Travel & Places": "travel",
    "Politics": "politics",
    "History": "history",
    "Education": "education",
    "Finance & Investing": "finance",
    "Automobiles": "autos",
    "Photography": "photo",
    "Pets & Animals": "pets",
    "Hobbies & Crafts": "hobbies",
    "Philosophy": "philosophy",
    "Religion & Spirituality": "religion",
    "Current Events": "news",
    "DIY & Home Improvement": "diy",
    "Software & Hardware": "tech",
    "Gaming Hardware": "hardware",
    "Collectibles": "collectibles",
    "Comics": "comics",
    "Lifestyle": "lifestyle",
    "Requests to Admin": "request_admin"
}

boards = []


def add_to_board_list():
    for board in BOARDS:
        board = BOARDS.get(board)
        boards.append(board)

add_to_board_list()



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# literally took hours to figure out by myself.
# this dynamic routing method allows users to visit differnt routes with different data
@app.route("/<board>", methods=["GET", "POST"])
def board(board):
    if board in boards:
        if request.method == "GET":
            posts = db.execute("SELECT * FROM posts WHERE board_name = ? ORDER BY timestamp DESC", board)
            replies = db.execute("SELECT * FROM replies ORDER BY timestamp DESC")
            return render_template("index.html", board_title=board, boards=boards, posts=posts, replies=replies, head_list_show=True, allow_new_thread=True)
        if request.method == "POST":
            title = request.form.get("title")
            content = request.form.get("content")
            file_exists, filename, filepath = get_uploaded_file("file")
            if file_exists:
                if 'passkey' in session:
                    user_uuid = get_user_uuid()
                    insert_into_posts(title=title, content=content,
                                    filename=filename, filepath=filepath, user_uuid=user_uuid, board_name=board)
                    flash("Post Created!")
                else:
                    insert_into_posts(title=title, content=content,
                                    filename=filename, filepath=filepath, board_name=board)
            else:
                if 'passkey' in session:
                    user_uuid = get_user_uuid()
                    insert_into_posts(
                        title=title, content=content, user_uuid=user_uuid, board_name=board)
                    flash("Post Created!")
                else:
                    insert_into_posts(title=title, content=content, board_name=board)
            return redirect("/"+board)
    else:
        return 'board does not exist'


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("boards.html", boards=boards)


@app.route("/reply", methods=["POST"])
def reply():
    if request.method == "POST":
        reply_post_id = request.form.get("reply_post_id")
        board_name = request.form.get("board_name")
        reply = request.form.get("reply")
        file_exists, filename, filepath = get_uploaded_file("file")
        if file_exists:
            if 'passkey' in session:
                user_uuid = get_user_uuid()
                insert_into_replies(reply_post_id=reply_post_id, reply=reply, filename=filename, filepath=filepath, user_uuid=user_uuid)
                flash("Replied!")

            else:
                insert_into_replies(reply_post_id=reply_post_id, reply=reply, filename=filename, filepath=filepath)
        else:
            if 'passkey' in session:
                user_uuid = get_user_uuid()
                insert_into_replies(reply_post_id=reply_post_id, reply=reply, user_uuid=user_uuid)
                flash("Replied!")
            else:
                insert_into_replies(reply_post_id=reply_post_id, reply=reply)
        return redirect("/"+board_name)



@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        passkey = request.form.get("passkey")
        user_uuid = str(uuid.uuid4())
        insert_into_users(passkey=passkey, user_uuid=user_uuid)
        session["passkey"] = passkey
    return redirect("/")


@app.route("/myposts")
def myposts():
    if 'passkey' in session:
        user_uuid = get_user_uuid()
        replies = db.execute("SELECT * FROM replies ORDER BY timestamp DESC")
        user_posts = db.execute("SELECT * FROM posts WHERE id IN (SELECT post_id FROM user_posts WHERE user_uuid = ?) ORDER BY timestamp DESC", user_uuid)
        return render_template("myposts.html", boards=boards, posts=user_posts, replies=replies, allow_new_thread=False, head_list_show=True)


@app.route("/myreplies")
def myreplies():
    if 'passkey' in session:
        user_uuid = get_user_uuid()
        user_replies = db.execute(
            "SELECT * FROM replies WHERE user_uuid = ? ORDER BY timestamp DESC", user_uuid)
        replied_posts = db.execute(
            "SELECT * FROM posts WHERE id IN (SELECT reply_post_id FROM replies WHERE user_uuid = ?) ORDER BY timestamp DESC", user_uuid)
        return render_template("myreplies.html", boards=boards, posts=replied_posts, replies=user_replies, allow_new_thread=False, head_list_show=True)


@app.route("/savepost/<int:post_id>", methods=["POST"])
def savepost(post_id):
    db.execute("UPDATE posts SET savedByMe = ? WHERE id = ?", 1, post_id)
    return jsonify({
        'type': 'saved',
        'status': 'success'
    })

@app.route("/unsavepost/<int:post_id>", methods=["POST"])
def unsavepost(post_id):
    db.execute("UPDATE posts SET savedByMe = ? WHERE id = ?", 0, post_id)
    return jsonify({
        'type': 'unsave',
        'status': 'success'
    })

@app.route("/savedposts")
def savedposts():
    saved_posts = db.execute("SELECT * FROM posts WHERE savedByMe = 1 ORDER BY timestamp DESC")
    replies = db.execute("SELECT * FROM replies ORDER BY timestamp DESC")
    return render_template("/index.html", board_title="saved posts", boards=boards, posts=saved_posts, replies=replies, allow_new_thread=False, head_list_show=True)


# asked some advice from chatGPT and adjusted as needed
@app.route('/vote/<int:post_id>/<string:action>', methods=['POST'])
def vote(post_id, action):
    user_uuid = get_user_uuid()
    upvoters_list = []
    downvoters_list = []
    upvoters = db.execute("SELECT upvoter FROM upvoters WHERE post_id = ?", post_id)
    downvoters = db.execute("SELECT downvoter FROM downvoters WHERE post_id = ?", post_id)
    for upvoter in upvoters:
        upvoters_list.append(upvoter['upvoter'])
    for downvoter in downvoters:
        downvoters_list.append(downvoter['downvoter'])
    if action == 'upvote':
        if session['passkey'] and user_uuid not in upvoters_list:
            insert_into_upvotes(post_id=post_id, upvoter=user_uuid)
            db.execute("UPDATE posts SET upvotes = upvotes + 1 WHERE id = ?", post_id)
            db.execute("UPDATE posts SET isVotedByMe = ? WHERE id = ?", 1, post_id)

    elif action == 'undo_upvote':
        if session['passkey'] and user_uuid in upvoters_list:
            remove_from_upvotes(post_id=post_id, upvoter=user_uuid)
            db.execute("UPDATE posts SET upvotes = upvotes - 1 WHERE id = ?", post_id)
            db.execute("UPDATE posts SET isVotedByMe = ? WHERE id = ?", 0, post_id)

    elif action == 'downvote':
        if session['passkey'] and user_uuid not in downvoters_list:
            insert_into_downvotes(post_id=post_id, downvoter=user_uuid)
            db.execute(
            "UPDATE posts SET downvotes = downvotes + 1 WHERE id = ?", post_id)
            db.execute("UPDATE posts SET isDownvotedByMe = ? WHERE id = ?", 1, post_id)

    elif action == 'undo_downvote':
        if session['passkey'] and user_uuid in downvoters_list:
            remove_from_downvotes(post_id=post_id, downvoter=user_uuid)
            db.execute(
            "UPDATE posts SET downvotes = downvotes - 1 WHERE id = ?", post_id)
            db.execute("UPDATE posts SET isDownvotedByMe = ? WHERE id = ?", 0, post_id)

    # Fetch the updated post to return the new values
    post = db.execute(
        "SELECT upvotes, downvotes FROM posts WHERE id = ?", post_id)[0]

    return jsonify({
        'upvotes': post['upvotes'],
        'downvotes': post['downvotes']
    })


def insert_into_upvotes(post_id, upvoter):
    db.execute("INSERT INTO upvoters (post_id, upvoter) VALUES(?, ?)",
               post_id, upvoter)


def remove_from_upvotes(post_id, upvoter):
    db.execute(
        "DELETE FROM upvoters WHERE post_id = ? AND upvoter = ?", post_id, upvoter)


def insert_into_downvotes(post_id, downvoter):
    db.execute(
        "INSERT INTO downvoters (post_id, downvoter) VALUES(?, ?)", post_id, downvoter)


def remove_from_downvotes(post_id, downvoter):
    db.execute(
        "DELETE FROM downvoters WHERE post_id = ? AND downvoter = ?", post_id, downvoter)


# get user_uuid
def get_user_uuid():
        if session["passkey"]:
            user = db.execute(
                "SELECT * FROM users WHERE passkey = ?", session["passkey"])[0]
            user_uuid = user['user_uuid']
            return user_uuid


def insert_into_posts(title, content, board_name, filename=None, filepath=None, user_uuid=None):
    # inserting into posts was painful so I simplified
    db.execute("INSERT INTO posts (title, content, board_name, filename, filepath, user_uuid, timestamp) VALUES(?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
               title, content, board_name, filename, filepath, user_uuid)
    if user_uuid and filename and filepath:
        post_id = db.execute("SELECT id FROM posts WHERE title=? AND content=? AND filename=? AND filepath=? AND user_uuid=? AND board_name=?", title, content, filename, filepath, user_uuid, board_name)[0]['id']
        db.execute("INSERT INTO user_posts (post_id, user_uuid) VALUES(?, ?)", post_id, user_uuid)
    elif user_uuid and not filename and not filepath:
        post_id = db.execute("SELECT id FROM posts WHERE title=? AND content=? AND user_uuid=? AND board_name=?", title, content, user_uuid, board_name)[0]['id']
        db.execute("INSERT INTO user_posts (post_id, user_uuid) VALUES(?, ?)", post_id, user_uuid)


def get_uploaded_file(element):
    file = request.files[element]
    file_exists = False
    if file and file.filename != '' and 'file' in request.files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_exists = True
        return file_exists, filename, filepath
    return False, None, None


def insert_into_replies(reply_post_id, reply, filename=None, filepath=None, user_uuid=None):
    # inserting into replies was painful so I simplified
    db.execute("INSERT INTO replies (reply_post_id, reply, filename, filepath, user_uuid, timestamp) VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
               reply_post_id, reply, filename, filepath, user_uuid)


def insert_into_users(passkey, user_uuid):
    db.execute("INSERT INTO users (passkey, user_uuid) VALUES(?, ?)",
               passkey, user_uuid)
