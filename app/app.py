from flask import Flask, render_template, request, redirect, url_for
from helpers import parse_raw_data
import zipfile

app = Flask(__name__)

# default page


@app.route('/')
def index():
    return render_template("index.html")

# upload's from index


@app.route('/', methods=['POST'])
def data_upload():
    file = request.files['file']
    # TODO: SETUP FILE EXCEPTIONS AND ERRORS

    zipfile_ = zipfile.ZipFile(file, "r")
    parsed_data = parse_raw_data(zipfile_)

    print(parsed_data)

    return redirect(url_for('analysis'))


@app.route('/analysis')
def analysis():
    # for now
    return render_template("dashboard.html")


# run app
app.run(
    debug=True
)
