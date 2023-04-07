from flask import Flask, render_template, request, redirect, url_for
from app.helpers import parse_raw_data
from analysis import DataAnalyzer
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

    analyzer = DataAnalyzer(parsed_data)
    print(analyzer.content.no_of_pfp_changes())

    return redirect(url_for('analysis'))


@app.route('/analysis')
def analysis():
    # for now
    return render_template("dashboard.html")


# run app
app.run(
    debug=True
)
