from flask import Flask, redirect, render_template, url_for,  request, flash, g
import db
from user_login import UserLogin
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from validators import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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
    # Create database object before request
    global database
    database = db.BlogApp_DB()

@login_manager.user_loader
def load_user(uid):
    # Login user with userID
    return UserLogin().from_db(user_id=uid, db=database)

@app.route('/unlike/<redirect_username>/<int:postid>')
@login_required
def unlike(redirect_username, postid: int):
    # Remove like from post with a specific id
    database.delete_like(username=current_user.get_username(), postid=postid)

    # Redirect to the last visited page
    return redirect(url_for("feed", username=redirect_username))

@app.route('/like/<redirect_username>/<int:postid>')
@login_required
def like(redirect_username, postid: int):
    # Add like to the post with a specific id
    database.add_like(username=current_user.get_username(), postid=postid)

    # Redirect to the last visited page
    return redirect(url_for("feed", username=redirect_username))

@app.route("/feed/<username>", methods=["GET", "POST"])
@login_required
def feed(username):
    # Create instances of the search user form and create post form
    search_user_form = SearchUserForm(request.form)
    create_post_form = CreatePostForm(request.form)

    # Get the profile picture source for the user
    profile_picture_src = current_user.get_profile_picture_src()

    # Check if there's any data sent by POST method
    if request.method == "POST":

        # Check if create post form was submitted
        if "create_post_submit" in request.form.keys():

            # Set up post content
            title = create_post_form.title.data
            content = create_post_form.content.data

            # Check post for validity errors (all fields are filled etc.)
            post_validation_error = check_post_validity(title=title, content=content)

            # Show flash notification if there's any errors
            if post_validation_error:
                flash(post_validation_error, category="error")
            else:

                # If there's no errors creating user post and adding it to database
                database.create_post(creator=current_user.get_username(),
                                     title=title,
                                     content=content
                                     )

                # Clear create post form fields
                create_post_form.content.data = ""
                create_post_form.title.data = ""
        elif "search_user_submit" in request.form.keys():

            # If user sends a username to search other user page
            # Check if entered username valid
            username_validation_error = check_username_validity(username=search_user_form.username.data)

            # Show error flash notification if there're any errors
            if username_validation_error:
                flash(username_validation_error, category="error")
            else:

                # If no errors found receiving user from database
                user_exists = database.get_user(username=search_user_form.username.data)

                # If user with searching username doesn't exists notifying user about it
                if not user_exists:
                    flash("User does not exists!", category="error")
                else:
                    # If searching user exists redirecting to searching user feed
                    return redirect(url_for("feed", username=search_user_form.username.data))

    # Get posts of needed user
    posts = database.get_user_posts(username=username)

    # Obtain likes that user made
    user_likes = database.get_user_likes(username=current_user.get_username())

    # Render user's feed
    return render_template(template_name_or_list="feed.html",
                           search_user_form=search_user_form,
                           create_post_form=create_post_form,
                           username=username,
                           profile_picture_src=profile_picture_src,
                           menu_items=menu_items,
                           user_likes=user_likes,
                           posts=posts,
                           title="Feed"
                            )


@app.route("/logout")
@login_required
def logout():
    # Logout user
    logout_user()

    # Redirect to home page
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    # Create update form instance
    profile_update = UpdateProfileForm(request.form)

    # Check if there's any data sent by POST method
    if request.method == "POST":

        # Set up new username
        username = profile_update.new_username.data

        # Check if user want to check username
        if username:

            # Catch validity errors
            username_valid_error = check_username_validity(username=username)

            # Check if there's user with new username
            username_exists_error = database.get_user(username=username)

            if not username_valid_error:
                if not username_exists_error:

                    # If there're no errors, update username and log user out to update UserLogin instance
                    database.update_username(userid=int(current_user.get_id()),
                                             new_username=username)
                    flash("Success. Log in to apply changes!", category="success")
                    logout()

                    # Reditect to the home page
                    return redirect(url_for("index"))
                else:

                    # Notifying user about Username Exists error
                    flash("Username already exists!", category="error")
            else:

                # Notifying user about Username Validity error
                flash(username_valid_error, category="error")

        # Set up new password
        new_password = profile_update.new_password.data

        if new_password:
            # If new password specified also get old password
            # and new password confirm (repeat)
            old_password = profile_update.old_password.data
            rnew_password = profile_update.rnew_password.data

            # Check old password accuracy
            if check_password_hash(current_user.get_password_hash(), old_password):

                # Check for new password validity errors
                new_password_validity_error = check_password_validity(new_password, rnew_password)

                if not new_password_validity_error:
                    # If there're no errors, update password and log user out to update UserLogin instance
                    new_password = generate_password_hash(password=new_password)
                    database.update_password(password=new_password, userid=current_user.get_id())
                    flash("Password changed successfully!", category="success")
                    logout()

                    # Redirect to the home page
                    return redirect(url_for("index"))
                else:

                    # Notify user about password validity error
                    flash(new_password_validity_error, category="error")
            else:
                # Notify user to check old password accuracy
                flash("Double check old password!", category="error")


    return render_template("settings.html",
                           menu_items=menu_items,
                           profile_picture_src=current_user.get_profile_picture_src(),
                           update_form=profile_update,
                           username=current_user.get_username()
                           )

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Create Signup form instance
    form = SignupForm(request.form)

    # Check if there's any data sent by POST method
    if request.method == "POST":

        # Check signup data for validity errors
        validity_errors = (check_password_validity(pwd=form.password.data,
                                                   rpwd=form.rpassword.data),
                           check_username_validity(username=form.username.data))
        validity_errors = tuple(filter(lambda x: x, validity_errors))

        if not validity_errors:

            # If passwords are same and there's no validity errors
            # Obtain password hash
            pwd_hash = generate_password_hash(password=form.password.data)

            # Set default picture path
            profile_picture_src = url_for("static", filename=f"profile_img/default.png")

            # Try to add a new user, and save any error message
            user_exists_error = database.add_user(form.username.data, pwd_hash, profile_picture_src=profile_picture_src)

            if user_exists_error:

                # Notify user if username is already taken
                flash(user_exists_error, category="error")
            else:

                # Notify about successfull signup
                flash("Signed up successfully!", category="success")

                # Redirect to the home page
                return redirect(url_for("index"))
        else:

            # Notify user about validity errors
            for error in validity_errors:
                if error:
                    flash(error, category="error")

    return render_template("signup.html", title="Sign Up", form=form)

@app.errorhandler(404)
def error_404(error):

    # Render page doesn't exist page
    return render_template("404.html", title="Not Found")

@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():

    # Reditect user to feed if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("feed", username=current_user.get_username()))

    # Create Login form instance
    form = LoginForm(request.form)

    # Check if there's any data sent by POST method
    if request.method == "POST":

        # Check if there's any user with entered username
        user = database.get_user(form.username.data)

        if user:

            # If user exists set user as a first match from the request result
            user = user[0]

            if check_password_hash(user["password"], form.password.data):

                # If passwords match log user in and redirect to the feed
                user_login = UserLogin().login(user=user)
                login_user(user=user_login)
                return redirect(url_for("feed", username=current_user.get_username()))
            else:

                # Notify user about wrong password
                flash("Double check your password!", category="error")

        else:

            # Notify user to check username twice
            flash("No user with such username", category="error")

    return render_template("index.html", title="Log In", form=form)

@app.route("/delete_user")
def delete_user():
    database.delete_user(username=current_user.get_username())
    flash("We're sorry you're leaving... Your account deleted. ", category="success")
    logout_user()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0")
