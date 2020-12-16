from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort,
)
from app import app
import os
import markdown
import codecs
from bracket_table.bracket_table import BracketTable

mod_avar = Blueprint("avar", __name__, template_folder="templates")

testing = app.config["AVAR_TEST"]
if not testing:
    host = "avar.rocks"
else:
    host = "localhost:5000"

##########
# Routes #
##########


@mod_avar.route("/favicon.ico", host=host)
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "avar_rocks/images"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_avar.route("/css/<path:css>", host=host)
def css(css):
    return send_from_directory(os.path.join(app.root_path, "avar_rocks/css"), css)


@mod_avar.route("/images/<image>", host=host)
def image(image):
    return send_from_directory(os.path.join(app.root_path, "avar_rocks/images"), image)


@mod_avar.route("/files/<doc>", methods=["GET"], host=host)
def download(doc):
    return send_from_directory("avar_rocks/files", doc)


@mod_avar.route("/", methods=["GET"], host=host)
def index():
    page = "avar_rocks/index.md"
    banner = "РорчIами!"
    html = get_html(page)
    return render_template("page_base.html", banner=banner, html=html)


@mod_avar.route("/<title>", methods=["GET"], host=host)
def page(title):
    page = "avar_rocks/%s.md" % title
    html = get_html(page)
    banners = {
        "resources": "resources",
        "grammar": "grammar",
        "textbook": "video textbook",
        "phrasebook": "phrasebook",
        "projects": "projects",
    }
    if html == "<p>404</p>":
        return abort(404)
    return render_template("page_base.html", banner=banners[title], html=html)


def get_html(md_text):
    filepath = os.path.join(app.root_path, md_text)
    try:
        input_file = codecs.open(filepath, mode="r", encoding="utf-8")
        text = input_file.read()
    except:
        text = "404"
    return markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.nl2br",
            "markdown.extensions.toc",
            "markdown.extensions.tables",
            "markdown.extensions.def_list",
            "markdown.extensions.abbr",
            "markdown.extensions.footnotes",
            BracketTable(),
            "doctor_leipzig.doctor_leipzig",
            "avar_rocks.flask.examples",
        ],
    )
