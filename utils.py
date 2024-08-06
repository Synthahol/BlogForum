import os

import bleach
import docx
import pandas as pd
import pypandoc
from flask import current_app
from linkify_it import LinkifyIt
from markdown import markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from odf.opendocument import load as load_odf
from odf.table import Table, TableCell, TableRow
from odf.text import P
from werkzeug.utils import secure_filename

from models import Media, db


class LinkifyPostprocessor(Postprocessor):
    def __init__(self, md):
        super().__init__(md)
        self.linkify = LinkifyIt()

    def run(self, text):
        matches = self.linkify.match(text)
        if not matches:
            return text

        matches.reverse()  # Process matches in reverse order to avoid offset issues

        for match in matches:
            start, end = match.index, match.last_index
            url = match.url
            link_html = f'<a href="{url}">{url}</a>'
            text = text[:start] + link_html + text[end:]
        return text


class LinkifyExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(LinkifyPostprocessor(md), "linkify", 175)


def allowed_file(filename):
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
        "csv",
        "doc",
        "docs",
        "ods",
        "odt",
        "rtf",
        "docx",
    }
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_media(form_media, user_id, post_id=None):
    filename = secure_filename(form_media.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    form_media.save(file_path)  # Save the file to the filesystem

    new_media = Media(
        filename=filename,
        filetype=form_media.content_type,  # Set the filetype
        user_id=user_id,
        post_id=post_id,
    )

    db.session.add(new_media)
    db.session.commit()

    return new_media.id  # Return the ID of the new media


def read_spreadsheet(file_path):
    ext = file_path.rsplit(".", 1)[1].lower()
    if ext in ["xls", "xlsx"]:
        return pd.read_excel(file_path).to_html()
    elif ext == "csv":
        return pd.read_csv(file_path).to_html()
    else:
        return "Unsupported file format"


def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


def read_odt(file_path):
    doc = load_odf(file_path)
    all_paras = []
    for element in doc.getElementsByType(P):
        all_paras.append("".join([str(text) for text in element.childNodes]))
    return "\n".join(all_paras)


def read_ods(file_path):
    doc = load_odf(file_path)
    tables = doc.getElementsByType(Table)
    data = []
    for table in tables:
        for row in table.getElementsByType(TableRow):
            row_data = [str(cell) for cell in row.getElementsByType(TableCell)]
            data.append("\t".join(row_data))
    return "\n".join(data)


def read_rtf(file_path):
    return pypandoc.convert_file(file_path, "plain")


def delete_media_file(media_id):
    media = Media.query.get(media_id)
    if media:
        db.session.delete(media)
        db.session.commit()


def is_image_file(filename):
    image_extensions = {"png", "jpg", "jpeg", "gif", "tiff", "tif", "svg"}
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in image_extensions


def sanitize_content(content):
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ["a"]
    allowed_attributes = {
        "a": ["href", "title", "target"],
    }
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=["http", "https"],
    )


def sanitize_and_render_markdown(content):
    # Use markdown.markdown() to convert Markdown to HTML with custom Linkify extension
    html_content = markdown(
        content, extensions=["extra", "sane_lists", LinkifyExtension()]
    )
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ["a", "pre", "code"]
    allowed_attributes = {"a": ["href", "rel", "title"]}
    sanitized_html = bleach.clean(
        html_content, tags=allowed_tags, attributes=allowed_attributes, strip=True
    )
    return sanitized_html
