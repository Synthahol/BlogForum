from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

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
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    media = FileField(
        "Upload File",
        validators=[
            FileAllowed(ALLOWED_EXTENSIONS, "Only specific file types are allowed!")
        ],
    )
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment = TextAreaField("Comment:", validators=[DataRequired()])
    submit = SubmitField("Submit")
