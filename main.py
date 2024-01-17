from flask import Flask, redirect, render_template, url_for,  request, flash, g
import db
from user_login import UserLogin
from forms import LoginForm, SignupForm, SearchUserForm, CreatePostForm
from werkzeug.security import generate_password_hash, check_password_hash
from validators import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import psycopg2
import os
import uuid


database = ""
SECRET_KEY = str(uuid.uuid4())
DEBUG = True


app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager(app=app)
login_manager.login_view = "index"
login_manager.login_message = "Log in to view this page!"
login_manager.login_message_category = "error"


@app.teardown_appcontext
def close_database(error):
    if hasattr(g, "link_db"):
        g.link_db.close()

def get_db_conn():
    conn = psycopg2.connect(dbname="BlogApp",
                            user=os.getenv("PostgreUSR"),
                            password=os.getenv("PostgrePWD"),
                            host="localhost"
                            )

    return conn

@app.before_request
def create_db():
    global database
    dbase_connection = connect_to_database()
    database = db.BlogApp_DB(conn=dbase_connection)

def connect_to_database():
    if not hasattr(g, "link_db"):
        g.link_db = get_db_conn()

    return g.link_db


@login_manager.user_loader
def load_user(uid):
    return UserLogin().from_db(user_id=uid, db=database)

@app.route('/unlike/<redirect_username>/<int:postid>')
@login_required
def unlike(redirect_username, postid: int):
    database.delete_like(username=current_user.get_username(), postid=postid)

    return redirect(url_for("feed", username=redirect_username))

@app.route('/like/<redirect_username>/<int:postid>')
@login_required
def like(redirect_username, postid: int):
    database.add_like(username=current_user.get_username(), postid=postid)

    return redirect(url_for("feed", username=redirect_username))

@app.route("/feed/<username>", methods=["GET", "POST"])
@login_required
def feed(username):
    search_user_form = SearchUserForm(request.form)
    create_post_form = CreatePostForm(request.form)

    visited_page_username = username

    if request.method == "POST":
        if "create_post_submit" in request.form.keys():
            title = create_post_form.title.data
            content = create_post_form.content.data

            post_validation_error = check_post_validity(title=title, content=content)

            if post_validation_error:
                flash(post_validation_error, category="error")
            else:
                database.create_post(creator=current_user.get_username(),
                                     title=title,
                                     content=content
                                     )
                username = current_user.get_username()

                create_post_form.content.data = ""
                create_post_form.title.data = ""
        elif "search_user_submit" in request.form.keys():
            username_validation_error = check_username_validity(username=search_user_form.username.data)
            if username_validation_error:
                flash(username_validation_error, category="error")
            else:
                return redirect(url_for("feed", username=search_user_form.username.data))

    posts = database.get_user_posts(username=username)
    user_likes_tuples = database.get_user_likes(username=current_user.get_username())
    user_likes = [like[0] for like in user_likes_tuples]
    print(user_likes)

    return render_template(template_name_or_list="feed.html",
                           search_user_form=search_user_form,
                           create_post_form=create_post_form,
                           username=current_user.get_username(),
                           visited_page_username=visited_page_username,
                           user_likes=user_likes,
                           posts=posts,
                           title="Feed"
                            )




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
def settings():
    return render_template("settings.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)
    if request.method == "POST":
        validity_errors = (check_password_validity(psw=form.password.data), check_username_validity(username=form.username.data))
        validity_errors = tuple(filter(lambda x: x, validity_errors))
        passwords_are_same = form.password.data == form.rpassword.data
        if not validity_errors:
            if passwords_are_same:
                pwd_hash = generate_password_hash(password=form.password.data)

                error = database.add_user(form.username.data, pwd_hash)

                if error:
                    flash(error, category="error")
                else:
                    flash("Signed up successfully!", category="success")
                    return render_template("index.html", title="Log In", form=LoginForm())
            else:
                flash("Passwords doesn't match!", category="error")
        else:
            for error in validity_errors:
                if error:
                    flash(error, category="error")

    return render_template("signup.html", title="Sign Up", form=form)

@app.errorhandler(404)
def error_404(error):
    return render_template("404.html", title="Not Found")

@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():

    if current_user.is_authenticated:
        return redirect(url_for("feed", username=current_user.get_username()))
    form = LoginForm(request.form)

    if request.method == "POST":
        user = database.get_user(form.username.data)
        if user:
            user = user[0]
            print(user)
            if check_password_hash(user["password"], form.password.data):
                user_login = UserLogin().login(user=user)
                login_user(user=user_login)
                return redirect(url_for("feed", username=current_user.get_username()))

            flash("Double check your password!", category="error")
        else:
            flash("No user with such username", category="error")

    return render_template("index.html", title="Log In", form=form)


if __name__ == "__main__":
    app.run(debug=DEBUG)
