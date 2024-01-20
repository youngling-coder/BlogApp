from flask import Flask, redirect, render_template, url_for,  request, flash, g
import db
from user_login import UserLogin
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from validators import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import psycopg2
import os
import uuid


database = ""
SECRET_KEY = str(uuid.uuid4())
DEBUG = True
menu_items = [{"name": "home", "url": "index"},
              {"name": "settings", "url": "settings"},
              {"name": "logout", "url": "logout"}
              ]

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


@app.before_request
def create_db():
    global database
    database = db.BlogApp_DB()

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

    profile_picture_src = current_user.get_profile_picture_src()

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
                user_exists = database.get_user(username=search_user_form.username.data)
                print(user_exists)
                if not user_exists:
                    flash("User does not exists!", category="error")
                else:
                    return redirect(url_for("feed", username=search_user_form.username.data))

    posts = database.get_user_posts(username=username)
    user_likes_tuples = database.get_user_likes(username=current_user.get_username())
    user_likes = [like[0] for like in user_likes_tuples]

    return render_template(template_name_or_list="feed.html",
                           search_user_form=search_user_form,
                           create_post_form=create_post_form,
                           username=username,
                           profile_picture_src=profile_picture_src,
                           visited_page_username=visited_page_username,
                           menu_items=menu_items,
                           user_likes=user_likes,
                           posts=posts,
                           title="Feed"
                            )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_profile_picture_src(username):
    return "." + url_for("static", filename=f"profile_img/{username}.png")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    profile_update = UpdateProfileForm(request.form)
    profile_picture_src = current_user.get_profile_picture_src()

    if request.method == "POST":

        username = profile_update.new_username.data
        username_valid_error = check_username_validity(username=username)
        username_exists_error = database.get_user(username=username)
        if username:
            if not username_valid_error:
                if not username_exists_error:
                    database.update_username(userid=int(current_user.get_id()),
                                             new_username=username)
                    flash("Success. Log in to apply changes!", category="success")
                    logout()
                    return redirect(url_for("index"))
                else:
                    flash("Username already exists!", category="error")
            else:
                flash(username_valid_error, category="error")


    return render_template("settings.html",
                           menu_items=menu_items,
                           profile_picture_src=profile_picture_src,
                           update_form=profile_update,
                           username=current_user.get_username()
                           )

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

                profile_picture_src = url_for("static", filename=f"profile_img/default.png")
                error = database.add_user(form.username.data, pwd_hash, profile_picture_src=profile_picture_src)

                if error:
                    flash(error, category="error")
                else:
                    flash("Signed up successfully!", category="success")
                    return redirect(url_for("index"))
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
