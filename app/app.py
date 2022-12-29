from flask import Flask, render_template, request, redirect, url_for
from helpers import transform_zipfile
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

    zipfile_ = zipfile.ZipFile(file)
    print(transform_zipfile(zipfile_)) 
    #TODO: SETUP FILE EXCEPTIONS AND ERRORS

    return redirect(url_for('analysis'))

@app.route('/analysis')
def analysis():
    # for now
    return render_template("dashboard.html")

# run app
app.run(
    debug=True
)