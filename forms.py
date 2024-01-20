from wtforms import *
from flask_wtf.file import FileAllowed
class UpdateProfilePicture(Form):
    picture = FileField(label="Upload any picture")

class SearchUserForm(Form):
    username = StringField(render_kw={
        "placeholder": "Enter username..."
        })


class CreatePostForm(Form):
    title = StringField(render_kw={
        "placeholder": "What's going on..."
        })
    content = TextAreaField(render_kw={
        "placeholder": "Add more details to your events..."
    })


class SignupForm(Form):
    username = StringField(validators=[validators.InputRequired(), validators.Length(max=32)], render_kw={
        "placeholder": "Create username..."
        })
    password = PasswordField(validators=[validators.InputRequired(), validators.Length(max=64)], render_kw={
        "placeholder": "Create password..."
        })
    rpassword = PasswordField(validators=[validators.InputRequired(), validators.Length(max=64)], render_kw={
        "placeholder": "Repeat password..."
        })


class LoginForm(Form):
    username = StringField(validators=[validators.InputRequired(), validators.Length(max=32)], render_kw={
        "placeholder": "Enter username..."
        })
    password = PasswordField(validators=[validators.InputRequired(), validators.Length(max=64)], render_kw={
        "placeholder": "Enter password..."
        })


class UpdateProfileForm(Form):
    file_input = FileField(label="Upload pic", render_kw={"id": "profile_picture_uploader"},validators=[
        FileAllowed(['image/*'])
    ])

    new_username = StringField(validators=[validators.Length(max=32)], render_kw={"placeholder": "Enter new username..."})
