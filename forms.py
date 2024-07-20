from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_wtf.recaptcha import RecaptchaField
from wtforms import HiddenField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import (  # noqa: F401
    URL,
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    Regexp,
    ValidationError,
)

from models import User

# List of allowed file extensions
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "tiff",
    "tif",
    "svg",
    "mp4",
    "avi",
    "avchd",
    "mov",
    "flv",
    "wmv",
    "mp3",
    "m4a",
    "wav",
    "pdf",
    "txt",
    "html",
    "xls",
    "xlsx",
    "ods",
    "doc",
    "docs",
    "docx",
}


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$",
                message="Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one number.",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$",
                message="Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one number.",
            ),
        ],
    )
    confirm_new_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Change Password")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    tags = StringField("Tags (comma separated)")
    media = FileField(
        "Upload File",
        validators=[
            FileAllowed(ALLOWED_EXTENSIONS, "Only specific file types are allowed!")
        ],
    )
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment = TextAreaField("", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UpdateProfileForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=150)]
    )
    bio = TextAreaField("Bio", validators=[Length(max=500)])
    avatar = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )
    submit = SubmitField("Update Profile")


class TagForm(FlaskForm):
    name = StringField("Tag Name", validators=[DataRequired()])
    submit = SubmitField("Save")


# Create Reaction Form
class ReactionForm(FlaskForm):
    post_id = HiddenField("post_id", validators=[DataRequired()])
    reaction_type = HiddenField("reaction_type", validators=[DataRequired()])
    submit = SubmitField("React")
