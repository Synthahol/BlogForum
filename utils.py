import os

import docx
import pandas as pd
import pypandoc
from flask import current_app
from odf.opendocument import load as load_odf
from odf.table import Table, TableCell, TableRow
from odf.text import P
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
