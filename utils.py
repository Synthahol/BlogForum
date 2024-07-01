import os

import docx
import pandas as pd
import pypandoc
from flask import current_app
from moviepy.editor import VideoFileClip
from odf.opendocument import load as load_odf
from odf.table import Table, TableCell, TableRow
from odf.text import P
from pdf2image import convert_from_path
from PIL import Image
from werkzeug.utils import secure_filename


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


def save_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join("uploads", filename))
    return filename


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


def save_media(form_media):
    filename = secure_filename(form_media.filename)
    file_path = os.path.join(current_app.root_path, "static/uploads", filename)
    form_media.save(file_path)
    return filename


def is_image_file(filename):
    image_extensions = {"png", "jpg", "jpeg", "gif", "tiff", "tif", "svg"}
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in image_extensions


def save_thumbnail(form_media, filename):
    ext = filename.split(".")[-1].lower()
    thumbnail_filename = f"thumb_{filename}"
    thumbnail_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], thumbnail_filename
    )

    try:
        if ext in ["jpg", "jpeg", "png", "gif", "tiff", "tif", "svg"]:
            with Image.open(form_media) as img:
                img.thumbnail((150, 150))
                img.save(thumbnail_path)
                current_app.logger.info(f"Image thumbnail created at {thumbnail_path}")
        elif ext in ["mp4", "avi", "avchd", "mov", "flv", "wmv"]:
            video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            current_app.logger.info(f"Processing video for thumbnail: {video_path}")
            if os.path.exists(video_path):
                clip = VideoFileClip(video_path)
                clip.save_frame(thumbnail_path, t=1.0)
                current_app.logger.info(f"Video thumbnail created at {thumbnail_path}")
            else:
                current_app.logger.error(f"Video file does not exist: {video_path}")
                thumbnail_filename = None
        elif ext == "pdf":
            pdf_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            current_app.logger.info(f"Processing PDF for thumbnail: {pdf_path}")
            if os.path.exists(pdf_path):
                pages = convert_from_path(pdf_path, 150)
                if pages:
                    pages[0].thumbnail((150, 150))
                    pages[0].save(thumbnail_path, "JPEG")
                    current_app.logger.info(
                        f"PDF thumbnail created at {thumbnail_path}"
                    )
                else:
                    current_app.logger.error(f"No pages found in PDF: {pdf_path}")
                    thumbnail_filename = None
            else:
                current_app.logger.error(f"PDF file does not exist: {pdf_path}")
                thumbnail_filename = None
        else:
            thumbnail_filename = None
            current_app.logger.warning(f"Unsupported file type for thumbnail: {ext}")

        if thumbnail_filename and os.path.exists(thumbnail_path):
            current_app.logger.info(f"Thumbnail saved: {thumbnail_filename}")
        else:
            current_app.logger.error(f"Thumbnail not created for {filename}")

    except Exception as e:
        current_app.logger.error(f"Error saving thumbnail: {e}")
        thumbnail_filename = None

    return thumbnail_filename
